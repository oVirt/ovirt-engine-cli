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
from ovirtcli.state.finitestatemachine import FiniteStateMachine

"""
    =========== define self instance ===========

    this is singleton instance of FiniteStateMachine
    that will be used across the app to maintain the
    state.

    =========== state optimization =============

    q ~  q` = {final states}, {other states}
        o

    q ~    q` <=> q~  q` and l(q,a) ~  l(q`,a)
       k+1          k                k

    ~   = ~ => ~  = ~
     k+1   k    k

    e.g:

        ---     =====     =====
      ->|1|-a-->||2||-a-->||3||----
        ---     =====     =====   |
         |      |   ^     |   ^   b
         b      |_b_|     |_a_|   |
         |        ^               |
         |        |               |
         v        a               |
        ---     __|__           =====
      ->|4|<--b-| 5 |<--------b-||6||-a--
      | ---     -----           =====   |
      |  |                        ^     |
      | a,b                       |_____|
      |__|


       1 2 3 4 5 6
      ------------
    a |2 3 3 4 2 6     ~  = {1,4,5}, {2,3,6}
    b |4 2 6 4 4 5      o
                       ~  = {1,5}, {2,3}. {4}, {6}
                        1

        ----      ====      ====
      ->|1,5|-a---||2||-a---||3||-b---
        ----      ====      ====     |
        |  ^      ^  |      ^   |    |
        b  |      |  b      |   a    |
        |  |      |__|      |___|    |
        |  |                         |
        |  |      ====               |
        |  -----b-||6||---------------
        V         ====
       ---        ^   |
       |4|-a,b-   |   a
       ---     |  |___|
        ^      |
        |      |
        |______|

"""

StateMachine = FiniteStateMachine(
    events=[
        DFSAEvent(
          name='exiting',
          sources=[
               DFSAState.Connecting,
               DFSAState.Connected,
               DFSAState.Disconnected,
               DFSAState.Unauthorized,
          ],
          destination=DFSAState.Exiting,
          callbacks=[]),
        DFSAEvent(
          name='disconnecting',
          sources=[
               DFSAState.Connected,
               DFSAState.Unauthorized,
               DFSAState.Exiting
          ],
          destination=DFSAState.Disconnecting,
          callbacks=[]),
        DFSAEvent(
          name='disconnected',
          sources=[
               DFSAState.Connected,
               DFSAState.Unauthorized,
               DFSAState.Disconnecting
          ],
          destination=DFSAState.Disconnected,
          callbacks=[]),
        DFSAEvent(
          name='connecting',
          sources=[
               DFSAState.Disconnected,
               DFSAState.Unauthorized
          ],
          destination=DFSAState.Connecting,
          callbacks=[]),
        DFSAEvent(
          name='connected',
          sources=[
               DFSAState.Disconnected,
               DFSAState.Unauthorized,
               DFSAState.Connecting
          ],
          destination=DFSAState.Connected,
          callbacks=[]),
        DFSAEvent(
          name='unauthorized',
          sources=[
               DFSAState.Connected
          ],
          destination=DFSAState.Unauthorized,
          callbacks=[]),
    ]
)
