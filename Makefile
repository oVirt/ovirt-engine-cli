all: rpm

rpmrelease:=1
rpmversion=3.3.0.4
RPMTOP=$(shell bash -c "pwd -P")/rpmtop
SPEC=ovirt-engine-cli.spec

TARBALL=ovirt-engine-cli-$(rpmversion).tar.gz
SRPM=$(RPMTOP)/SRPMS/ovirt-engine-cli-$(rpmversion)-$(rpmrelease)*.src.rpm

TESTS=pyflakes

test: pyflakes exceptions
	echo $(rpmrelease) $(rpmversion)

pyflakes:
	@git ls-files '*.py' | xargs pyflakes \
	    || (echo "Pyflakes errors or pyflakes not found"; exit 1)

.PHONY: tarball
tarball: $(TARBALL)
$(TARBALL): Makefile #$(TESTS)
	git config tar.umask 0022
	git archive --format=tar --prefix ovirt-engine-cli/ HEAD | gzip > $(TARBALL)

.PHONY: srpm rpm
srpm: $(SRPM)
$(SRPM): $(TARBALL) ovirt-engine-cli.spec.in
	sed 's/^Version:.*/Version: $(rpmversion)/;s/^Release:.*/Release: $(rpmrelease)%{dist}/;s/%{release}/$(rpmrelease)/' ovirt-engine-cli.spec.in > $(SPEC)
	mkdir -p $(RPMTOP)/{RPMS,SRPMS,SOURCES,BUILD}
	rpmbuild -bs \
	    --define="_topdir $(RPMTOP)" \
	    --define="_sourcedir ." $(SPEC)

rpm: $(SRPM)
	rpmbuild --define="_topdir $(RPMTOP)" --rebuild $<

clean:
	$(RM) *~ *.pyc ovirt-engine-cli*.tar.gz $(SPEC)
	$(RM) -r rpmtop
