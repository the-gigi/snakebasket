from snakebasket import versions
from nose.tools import assert_equal, assert_raises
from pip.exceptions import InstallationError
from pip.req import Requirements, InstallRequirement
from tests.test_pip import (here, reset_env, run_pip, pyversion, mkdir,
                            src_folder, write_file)
from tests.local_repos import local_checkout
from mock import Mock

def test_comparison():
    """ Comparison of version strings works for editable git repos """
    url_template = "git+http://github.com/prezi/sb-test-package.git@%s#egg=sb-test-package"
    test_project_name = "sb-test-package" 

    def make_install_req(ver=None):
        req = Mock()
        req.project_name = test_project_name
        if ver:
            req.url = url_template % str(ver)
            req.specs = [('==', ver)]
        else:
            req.url = url_template.replace('@','') % ''
            req.specs = []

        install_requirement = InstallRequirement(req, None, editable = True, url = req.url)

        return install_requirement

    reset_env()

    older_ver = '0.1'
    older_commit = '6e513083955aded92f1833ff460dc233062a7292'

    current_ver = '0.1.1'
    current_commit = 'bd814b468924af1d41e9651f6b0d4fe0dc484a1e'

    newer_ver = '0.1.2'
    newer_commit = '2204077f795580d2f8d6df82caee34126aaf87eb'

    head_alias = 'HEAD'
    master_alias = 'master'

    def new_req_checker(default_requirment):
        requirements = Requirements()
        requirements[default_requirment.name] = default_requirment
        checker = versions.InstallReqChecker('../sb-venv/source/%s' % test_project_name, requirements, [])
        return checker

    # version tags are compared as they should be:
    older_req = make_install_req(older_ver)
    current_req = make_install_req(current_ver)
    newer_req = make_install_req(newer_ver)

    checker = new_req_checker(current_req)

        # there should be an available substitute (current_req) for an older version
    assert_equal(
        current_ver,
        checker.get_available_substitute(older_req).version
    )
        # there souldn't be a substitute for a newer version 
    assert_equal(
        None,
        checker.get_available_substitute(newer_req)
    )

    # commit hashes are compared has they should be:
    older_req = make_install_req(older_commit)
    current_req = make_install_req(current_commit)
    newer_req = make_install_req(newer_commit)

    checker = new_req_checker(current_req)

        # there should be an available substitute (current_req) for an older version
    assert_equal(
        current_commit,
        checker.get_available_substitute(older_req).version
    )
        # there souldn't be a substitute for a newer version 
    assert_equal(
        None,
        checker.get_available_substitute(newer_req)
    )

    # different aliases of the same commit id appear to be equal:
    head_req = make_install_req(head_alias)
    master_req = make_install_req(master_alias)

    checker = new_req_checker(head_req)
    assert_equal(
        head_alias,
        checker.get_available_substitute(master_req).version
    )

    checker = new_req_checker(master_req)
    assert_equal(
        master_alias,
        checker.get_available_substitute(head_req).version
    )

    # Divergent branches should not be able to be compared
    def compare_two_different_branches():
        branch_a_req = make_install_req('test_branch_a')
        branch_b_req = make_install_req('test_branch_b')

        checker = new_req_checker(branch_a_req)
        checker.get_available_substitute(branch_b_req)

    assert_raises(InstallationError, compare_two_different_branches)

    # two unpinned versions of the same requirement should be equal:

    unpinned_req_1 = make_install_req()
    unpinned_req_2 = make_install_req()
    checker = new_req_checker(unpinned_req_1)

    assert checker.get_available_substitute(unpinned_req_2)

def test_requirement_set_will_include_correct_version():
    """ Out of two versions of the same package, the requirement set will contain the newer one. """
    reset_env()
    local_url = local_checkout('git+http://github.com/prezi/sb-test-package.git')
    args = ['install',
        # older version
        '-e', '%s@0.2.0#egg=sb-test-package' % local_url,
        # newer version
        '-e', '%s@0.2.1#egg=sb-test-package' % local_url]
    result = run_pip(*args, **{"expect_error": True})
    result.assert_installed('sb-test-package')
    v020 = 'sb-test-package 0.2.0'
    v021 = 'sb-test-package 0.2.1'
    assert not (v020 in result.stdout)
    assert v021 in result.stdout

def test_editable_reqs_override_pypi_packages():
    """ Not Implemented: If a conflicing editable and pypi package are given, the editable will be installed. """
    pass