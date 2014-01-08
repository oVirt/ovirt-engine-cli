#
# Copyright (c) 2013 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from ovirtcli.state.dfsaevent import DFSAEvent
from ovirtcli.state.dfsastate import DFSAState
from ovirtcli.annotations.requires import Requires
from ovirtcli.events.event import Event
from ovirtcli.meta.singleton import Singleton

from cli.error import StateError, UnknownEventError

class FiniteStateMachine(object):
    '''
    The Deterministic Finite-State Automata (DFSA)

    =========== state maintains logic ===========

    A=(A, Q, l, q0, F)

    A is alphabetic
                                 _
    Q is a finite set of states |_|
                                      _      _
    l is a state transition function |_| -> |_|
                             _
    q0 is a initial state ->|_|

                               =====
    F is a set of final states || ||
                               =====

    L = {ab^n E A* : n >= 0}


    e.g:

        --b-------------------------
        |                          |
       ---       =====      ----   |
     ->|q0|-a--->||q1||-a-->|q2|<---
        --       =====      ----
                 |   ^      |   ^
                 b   |     a,b  |
                 |   |      |   |
                 -----      -----

    A = ({{a, b}, {q0,q1,q2},l,{q0}, {q1})

    e.g: l=(q0,a)=q1 l=(q1,b)=q1

    =========== usage ===========

    from ovirtcli.state.finitestatemachine import FiniteStateMachine
    from ovirtcli.state.dfsaevent import DFSAEvent
    from ovirtcli.state.dfsastate import DFSAState

    1. define the callback for events, with callback you can either
       perform onEvent actions or block the StateMachine till your
       action is accomplished.

        def onConnectCallback(self, **kwargs):
            print "connect callback with:\n%s\n\n" % kwargs['event']

        def onDisconnectCallback(self, **kwargs):
            print "disconnect callback:\n%s\n\n" % kwargs['event']

    2. define the StateMachine

    class Test(object):
        def run(self):
            sm = FiniteStateMachine( # define the StateMachine
                events=[ # define events
                    DFSAEvent( # define StateMachine event
                      name='disconnect', # event name
                      sources=[ # source states from which this event is eligible
                           DFSAState.Connected,
                           DFSAState.Unauthorized
                      ],
                      destination=DFSAState.Disconnected, # destination event state
                      callbacks=[self.onDisconnectCallback]), # callbacks to invoke after
                                                              # this events is triggered
                    DFSAEvent(
                      name='connect',
                      sources=[
                           DFSAState.Disconnected,
                           DFSAState.Unauthorized
                      ],
                      destination=DFSAState.Connected,
                      callbacks=[self.onConnectCallback]),
                    DFSAEvent(
                      name='unauthorized',
                      sources=[
                           DFSAState.Connected
                      ],
                      destination=DFSAState.Unauthorized,
                      callbacks=[]),
                ]
            )

    3. StateMachine has own events:

       - onBeforeApplyState: triggered Before ApplyState occurs
       - onAfterApplyState : triggered After ApplyState occurs
       - onStateChange,    : triggered on any StateChange
       - onBeforeEvent     : triggered Before Event processed
       - onAfterEvent      : triggered After Event processed
       - onCanMove         : triggered when CanMove() check is invoked

       you can register to them using event patter:

       sm.onBeforeEvent += OnBeforeEventListener()

       NOTE:

       - EventListener must to implement IListener interface
       - All events are provided with 'event' argument to maintain the state
         between the events, in some case extra data can be provided such as
         [source, destination, result, ...] depending on event's context.
       - callbacks can be registered later calling sm.add_callback(DFSAState.X, your_method)

    4. trigger events on StateMachine

            sm.connect() # 'connect' event
            # print sm; print "\n"
            sm.disconnect() 'disconnect' event
            # print sm; print "\n"
            sm.unauthorized() 'unauthorized' event
            # print sm; print "\n"
            ...

    Test().run()
    '''

    __metaclass__ = Singleton

#   @Requires([DFSAEvent], DFSAEvent)
#   TODO: support multi-parameters definition ^
    def __init__(self, events, inital_state=DFSAEvent(
                                      name='disconnected',
                                      sources=[],
                                      destination=DFSAState.DISCONNECTED,
                                      description='init'
                               )
        ):
        '''
        @param events: the list of DFSA events
        @param inital_state: the inital state of DFSA (optional)
        '''

        assert events != None

        self.__id = id(self)
        self.__current_state_obj = None
        self.__current_state = None
        self.__origin_state = None
        self.__origin_state_object = None
        self.__events = {}  # future use

        self.onBeforeApplyState = Event()
        self.onAfterApplyState = Event()
        self.onStateChange = Event()

        self.onBeforeEvent = Event()
        self.onAfterEvent = Event()

        self.onCanMove = Event()

        self.__register_events(events)
        self.__resolve_inital_state(inital_state)

#     @Requires(DFSAEvent)
    def __apply_state(self, event):
        """
        applying state

        @raise StateError: when event.destination state is
                           not applicable from the current_state
        """
        if self.can_move(event):
            self.onBeforeApplyState.fire(
                     event=event,
                     source=self.get_current_state(),
                     destination=event.get_destination()
            )
            self.onStateChange.fire(
                     event=event,
                     source=self.get_current_state(),
                     destination=event.get_destination()
            )

            old_state = self.get_current_state()

            self.__origin_state_object = self.__current_state_obj
            self.__current_state_obj = event
            self.__origin_state = self.__current_state
            self.__current_state = event.get_destination()

            self.onAfterApplyState.fire(
                     event=event,
                     source=old_state,
                     destination=self.get_current_state()
            )

        else:
            self.__raise_state_error(event)

    @Requires([DFSAEvent])
    def __register_events(self, events):
        """
        registers events

        @param events: the list of events to register
        """
        self.__events = {}
        for event in events:
            self.__do_add_event(event)

#     @Requires(DFSAEvent)
    def __produce_event_method(self, event):
        """
        produces event method

        @param eevent: event for which the method should
                       be procured
        """
        def event_method(**kwargs):
            if self.get_current_state() != event.get_destination():
                self.onBeforeEvent.fire(event=event)
                self.__apply_state(event)
                if event.get_callbacks():
                    for callback in event.get_callbacks():
                        # TODO: consider passing all **kwargs
                        callback(event=event)
                self.onAfterEvent.fire(event=event)
            else:
                return
        return event_method

#     @Requires(DFSAEvent)
    def __raise_state_error(self, event):
        """
        @raise StateError: when event.destination state is
                           not applicable from the current_state
        """
        raise StateError(
                 destination=event,
                 current=self.get_current_state()
        )

    def __raise_unknown_event(self, name):
        """
        @raise UnknownEventError: when is not registered
        """
        raise UnknownEventError(name=name)

#     @Requires(DFSAEvent)
    def __do_add_event(self, event):
        """
        registers new event in DFSM

        @param event: event to register
        """
        self.__events[event.get_name()] = event
        setattr(
            self,
            event.get_name(),
            self.__produce_event_method(event)
        )

#     @Requires(types.StringType)
    def __get_event(self, state):
        name = str(DFSAState(state)).lower()
        if name in self.__events.keys():
            return self.__events[name]
        self.__raise_unknown_event(name)

    def __str__(self):
        return 'FiniteStateMachine: %s, current state: %s' % (
               str(self.__id),
               DFSAState(self.get_current_state())
        )

    @Requires(DFSAEvent)
    def add_event(self, event):
        """
        adds or overrides DFSAEvent event to/in DFSA

        @param event: the DFSAEvent to add/override
        """
        self.__do_add_event(event)

    # @Requires(types.StringType, types.MethodType)
    def add_callback(self, state, callback):
        """
        adds new callback to event

        @param state: the state to which you would
                      like to add a callback
        @param callback: the method to register
        """
        self.__get_event(state) \
            .get_callbacks() \
            .append(callback)

    def get_current_state(self):
        """
        @return: the current State of DFSA
        """
        return self.__current_state

    def get_origin_state(self):
        """
        @return: the origin State of DFSA
        """
        return self.__origin_state

    def get_origin_state_event(self):
        """
        @return: the origin State of DFSA
        """
        return self.__origin_state_object

    @Requires(DFSAEvent)
    def can_move(self, event):
        """
        checks if DFSA can move to the given event.destination

        @param event: the destination DFSAEvent
        """
        if not self.__current_state_obj:
            result = True  # can happen during init only!
            # TODO: consider restricting this behavior
        else:
            result = self.__current_state in event.get_sources()

        self.onCanMove.fire(
                 event=event,
                 source=self.get_current_state(),
                 destination=event.get_destination(),
                 result=result
        )

        return result

    def rollback(self):
        """
        performs a rollback to the origin state
        """
        self.__apply_state(self.get_origin_state_event())

    def __resolve_inital_state(self, inital_state):
        """
        resolves initial state of DFSA

        if user has defined same state as default one and DFSA can move to it -
        it will be used, otherwise default state will be set as a initial.
        """
        if self.__events.has_key(inital_state.get_name()) and \
           self.can_move(inital_state):
            self.__apply_state(
                   self.__events.get(
                         inital_state.get_name()
                   )
            )
        else:
            self.__apply_state(inital_state)
