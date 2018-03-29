# SPDX-License-Identifier: GPL-2.0+

import json


all_rpmdiff_testcase_names = [
    'dist.rpmdiff.analysis.abi_symbols',
    'dist.rpmdiff.analysis.binary_stripping',
    'dist.rpmdiff.analysis.build_log',
    'dist.rpmdiff.analysis.changes_in_rpms',
    'dist.rpmdiff.analysis.desktop_file_sanity',
    'dist.rpmdiff.analysis.elflint',
    'dist.rpmdiff.analysis.empty_payload',
    'dist.rpmdiff.analysis.execshield',
    'dist.rpmdiff.analysis.file_list',
    'dist.rpmdiff.analysis.file_permissions',
    'dist.rpmdiff.analysis.file_sizes',
    'dist.rpmdiff.analysis.ipv6',
    'dist.rpmdiff.analysis.java_byte_code',
    'dist.rpmdiff.analysis.kernel_module_parameters',
    'dist.rpmdiff.analysis.manpage_integrity',
    'dist.rpmdiff.analysis.metadata',
    'dist.rpmdiff.analysis.multilib_regressions',
    'dist.rpmdiff.analysis.ownership',
    'dist.rpmdiff.analysis.patches',
    'dist.rpmdiff.analysis.pathnames',
    'dist.rpmdiff.analysis.politics',
    'dist.rpmdiff.analysis.rpath',
    'dist.rpmdiff.analysis.rpm_changelog',
    'dist.rpmdiff.analysis.rpm_config_doc_files',
    'dist.rpmdiff.analysis.rpm_requires_provides',
    'dist.rpmdiff.analysis.rpm_scripts',
    'dist.rpmdiff.analysis.rpm_triggers',
    'dist.rpmdiff.analysis.shell_syntax',
    'dist.rpmdiff.analysis.specfile_checks',
    'dist.rpmdiff.analysis.symlinks',
    'dist.rpmdiff.analysis.upstream_source',
    'dist.rpmdiff.analysis.virus_scan',
    'dist.rpmdiff.analysis.xml_validity',
    'dist.rpmdiff.comparison.abi_symbols',
    'dist.rpmdiff.comparison.binary_stripping',
    'dist.rpmdiff.comparison.build_log',
    'dist.rpmdiff.comparison.changed_files',
    'dist.rpmdiff.comparison.changes_in_rpms',
    'dist.rpmdiff.comparison.desktop_file_sanity',
    'dist.rpmdiff.comparison.dt_needed',
    'dist.rpmdiff.comparison.elflint',
    'dist.rpmdiff.comparison.empty_payload',
    'dist.rpmdiff.comparison.execshield',
    'dist.rpmdiff.comparison.file_list',
    'dist.rpmdiff.comparison.file_permissions',
    'dist.rpmdiff.comparison.file_sizes',
    'dist.rpmdiff.comparison.files_moving_rpm',
    'dist.rpmdiff.comparison.file_types',
    'dist.rpmdiff.comparison.ipv6',
    'dist.rpmdiff.comparison.java_byte_code',
    'dist.rpmdiff.comparison.kernel_module_parameters',
    'dist.rpmdiff.comparison.kernel_module_pci_ids',
    'dist.rpmdiff.comparison.manpage_integrity',
    'dist.rpmdiff.comparison.metadata',
    'dist.rpmdiff.comparison.multilib_regressions',
    'dist.rpmdiff.comparison.ownership',
    'dist.rpmdiff.comparison.patches',
    'dist.rpmdiff.comparison.pathnames',
    'dist.rpmdiff.comparison.politics',
    'dist.rpmdiff.comparison.rpath',
    'dist.rpmdiff.comparison.rpm_changelog',
    'dist.rpmdiff.comparison.rpm_config_doc_files',
    'dist.rpmdiff.comparison.rpm_requires_provides',
    'dist.rpmdiff.comparison.rpm_scripts',
    'dist.rpmdiff.comparison.rpm_triggers',
    'dist.rpmdiff.comparison.shell_syntax',
    'dist.rpmdiff.comparison.specfile_checks',
    'dist.rpmdiff.comparison.symlinks',
    'dist.rpmdiff.comparison.upstream_source',
    'dist.rpmdiff.comparison.virus_scan',
    'dist.rpmdiff.comparison.xml_validity',
]

TASKTRON_RELEASE_CRITICAL_TASKS = [
    'dist.abicheck',
    'dist.rpmdeplint',
    'dist.upgradepath',
]

OPENQA_SCENARIOS = [
    'scenario1',
    'scenario2',
]


def test_inspect_policies(requests_session, greenwave_server):
    r = requests_session.get(greenwave_server.url + 'api/v1.0/policies',
                             headers={'Content-Type': 'application/json'})
    assert r.status_code == 200
    body = r.json()
    policies = body['policies']
    assert len(policies) == 6
    assert any(p['id'] == 'taskotron_release_critical_tasks' for p in policies)
    assert any(p['decision_context'] == 'bodhi_update_push_stable' for p in policies)
    assert any(p['product_versions'] == ['fedora-26'] for p in policies)
    expected_rules = [
        {'rule': 'PassingTestCaseRule',
         'test_case_name': 'dist.abicheck',
         'scenario': None},
    ]
    assert any(p['rules'] == expected_rules for p in policies)
    expected_rules = [
        {'rule': 'PassingTestCaseRule',
         'test_case_name': 'dist.rpmdeplint',
         'scenario': None},
        {'rule': 'PassingTestCaseRule',
         'test_case_name': 'dist.upgradepath',
         'scenario': None}]
    assert any(p['rules'] == expected_rules for p in policies)


def test_cannot_make_decision_without_product_version(requests_session, greenwave_server):
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'subject': [{'item': 'foo-1.0.0-1.el7', 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 400
    assert u'Missing required product version' == r.json()['message']


def test_cannot_make_decision_without_decision_context(requests_session, greenwave_server):
    data = {
        'product_version': 'rhel-7',
        'subject': [{'item': 'foo-1.0.0-1.el7', 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 400
    assert u'Missing required decision context' == r.json()['message']


def test_cannot_make_decision_without_subject(requests_session, greenwave_server):
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 400
    assert u'Missing required subject' == r.json()['message']


def test_cannot_make_decision_with_invalid_subject(requests_session, greenwave_server):
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': ['foo-1.0.0-1.el7'],
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 400
    assert u'Invalid subject, must be a list of dicts' in r.text


def test_404_for_inapplicable_policies(requests_session, greenwave_server):
    data = {
        'decision_context': 'dummy_decision',
        'product_version': 'rhel-7',
        'subject': [{'item': 'foo-1.0.0-1.el7', 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 404
    expected = u'Cannot find any applicable policies ' + \
        'for rhel-7 and dummy_decision'
    assert expected == r.json()['message']


def test_make_a_decison_on_passed_result(requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    for testcase_name in all_rpmdiff_testcase_names:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }

    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    assert res_data['applicable_policies'] == ['1']
    expected_summary = 'all required tests passed'
    assert res_data['summary'] == expected_summary


def test_make_a_decison_with_verbose_flag(requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    for testcase_name in all_rpmdiff_testcase_names:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}],
        'verbose': True,
    }

    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    expected_result = {
        u'data': {
            u'item': [u'glibc-1.0-2.el7'],
            u'type': [u'koji_build']
        },
        u'groups': [],
        u'href': u'http://localhost:5001/api/v2.0/results/72',
        u'id': 72,
        u'note': None,
        u'outcome': u'PASSED',
        u'ref_url': None,
        #u'submit_time': u'2018-01-28T12:55:54.641139',
        u'testcase': {
            u'href': u'http://localhost:5001/api/v2.0/testcases/dist.rpmdiff.analysis.abi_symbols',
            u'name': u'dist.rpmdiff.analysis.abi_symbols',
            u'ref_url': None,
        }
    }

    assert len(res_data['results']) == len(all_rpmdiff_testcase_names)
    del res_data['results'][-1]['submit_time']
    assert res_data['results'][-1] == expected_result
    expected_waivers = []
    assert res_data['waivers'] == expected_waivers


def test_make_a_decison_on_failed_result_with_waiver(
        requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    # First one failed but was waived
    result = testdatabuilder.create_result(item=nvr,
                                           testcase_name=all_rpmdiff_testcase_names[0],
                                           outcome='FAILED')
    waiver = testdatabuilder.create_waiver(result={ # noqa
        "subject": dict([(key, value[0]) for key, value in result['data'].items()]),
        "testcase": all_rpmdiff_testcase_names[0]}, product_version='rhel-7')
    # The rest passed
    for testcase_name in all_rpmdiff_testcase_names[1:]:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    assert res_data['applicable_policies'] == ['1']
    expected_summary = 'all required tests passed'
    assert res_data['summary'] == expected_summary


def test_make_a_decison_on_failed_result(requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    result = testdatabuilder.create_result(item=nvr,
                                           testcase_name='dist.rpmdiff.comparison.xml_validity',
                                           outcome='FAILED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is False
    assert res_data['applicable_policies'] == ['1']
    expected_summary = '1 of 71 required tests failed, 70 results missing'
    assert res_data['summary'] == expected_summary
    expected_unsatisfied_requirements = [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'result_id': result['id'],
            'testcase': 'dist.rpmdiff.comparison.xml_validity',
            'scenario': None,
            'type': 'test-result-failed'
        },
    ] + [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'testcase': name,
            'type': 'test-result-missing',
            'scenario': None,
        } for name in all_rpmdiff_testcase_names if name != 'dist.rpmdiff.comparison.xml_validity'
    ]
    assert sorted(res_data['unsatisfied_requirements']) == sorted(expected_unsatisfied_requirements)


def test_make_a_decison_on_no_results(requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is False
    assert res_data['applicable_policies'] == ['1']
    expected_summary = '71 of 71 required test results missing'
    assert res_data['summary'] == expected_summary
    expected_unsatisfied_requirements = [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'testcase': name,
            'type': 'test-result-missing',
            'scenario': None,
        } for name in all_rpmdiff_testcase_names
    ]
    assert res_data['unsatisfied_requirements'] == expected_unsatisfied_requirements


def test_unrestricted_policy_is_always_satisfied(
        requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'cdk-2',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    assert res_data['applicable_policies'] == ['errata-unrestricted']
    expected_summary = 'no tests are required'
    assert res_data['summary'] == expected_summary
    assert res_data['unsatisfied_requirements'] == []


def test_bodhi_push_update_stable_policy(
        requests_session, greenwave_server, testdatabuilder):
    nvr = testdatabuilder.unique_nvr()
    for testcase_name in TASKTRON_RELEASE_CRITICAL_TASKS:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'bodhi_update_push_stable',
        'product_version': 'fedora-26',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    assert 'taskotron_release_critical_tasks' in res_data['applicable_policies']
    assert 'taskotron_release_critical_tasks_with_blacklist' in res_data['applicable_policies']
    expected_summary = 'all required tests passed'
    assert res_data['summary'] == expected_summary
    assert res_data['unsatisfied_requirements'] == []


def test_multiple_results_in_a_subject(
        requests_session, greenwave_server, testdatabuilder):
    """
    This makes sure that Greenwave uses the latest test result when a subject has
    multiple test restuls.
    """
    nvr = testdatabuilder.unique_nvr()
    testdatabuilder.create_result(item=nvr,
                                  testcase_name='dist.abicheck',
                                  outcome='PASSED')
    # create one failed test result for dist.abicheck
    result = testdatabuilder.create_result(item=nvr,
                                           testcase_name='dist.abicheck',
                                           outcome='FAILED')
    # the rest passed
    for testcase_name in TASKTRON_RELEASE_CRITICAL_TASKS[1:]:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'bodhi_update_push_stable',
        'product_version': 'fedora-26',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    # The failed result should be taken into account.
    assert res_data['policies_satisfied'] is False
    assert 'taskotron_release_critical_tasks' in res_data['applicable_policies']
    assert 'taskotron_release_critical_tasks_with_blacklist' in res_data['applicable_policies']
    assert res_data['summary'] == '1 of 3 required tests failed'
    expected_unsatisfied_requirements = [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'result_id': result['id'],
            'testcase': 'dist.abicheck',
            'type': 'test-result-failed',
            'scenario': None,
        },
    ]
    assert res_data['unsatisfied_requirements'] == expected_unsatisfied_requirements


def test_ignore_result(requests_session, greenwave_server, testdatabuilder):
    """
    This tests that a result can be ignored when making the decision.
    """
    nvr = testdatabuilder.unique_nvr()
    result = testdatabuilder.create_result(
        item=nvr,
        testcase_name=TASKTRON_RELEASE_CRITICAL_TASKS[0],
        outcome='PASSED')
    for testcase_name in TASKTRON_RELEASE_CRITICAL_TASKS[1:]:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'bodhi_update_push_stable',
        'product_version': 'fedora-26',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    # Ignore one passing result
    data.update({
        'ignore_result': [result['id']]
    })
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    expected_unsatisfied_requirements = [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'testcase': TASKTRON_RELEASE_CRITICAL_TASKS[0],
            'type': 'test-result-missing',
            'scenario': None,
        },
    ]
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is False
    assert res_data['unsatisfied_requirements'] == expected_unsatisfied_requirements


def test_make_a_decison_on_passed_result_with_scenario(
        requests_session, greenwave_server, testdatabuilder):
    """
    If we require two scenarios to pass, and both pass, then we pass.
    """
    compose_id = testdatabuilder.unique_compose_id()
    testcase_name = 'compose.install_no_user'
    for scenario in OPENQA_SCENARIOS:
        testdatabuilder.create_compose_result(
            compose_id=compose_id,
            testcase_name=testcase_name,
            scenario=scenario,
            outcome='PASSED')
    data = {
        'decision_context': 'rawhide_compose_sync_to_mirrors',
        'product_version': 'fedora-rawhide',
        'subject': [{'productmd.compose.id': compose_id}],
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True
    assert res_data['applicable_policies'] == ['openqa_important_stuff_for_rawhide']
    expected_summary = 'all required tests passed'
    assert res_data['summary'] == expected_summary


def test_make_a_decison_on_failing_result_with_scenario(
        requests_session, greenwave_server, testdatabuilder):
    """
    If we require two scenarios to pass, and one is failing, then we fail.
    """

    compose_id = testdatabuilder.unique_compose_id()
    testcase_name = 'compose.install_no_user'
    # Scenario 1 passes..
    testdatabuilder.create_compose_result(
        compose_id=compose_id,
        testcase_name=testcase_name,
        scenario='scenario1',
        outcome='PASSED')
    # But scenario 2 fails!
    result = testdatabuilder.create_compose_result(
        compose_id=compose_id,
        testcase_name=testcase_name,
        scenario='scenario2',
        outcome='FAILED')
    data = {
        'decision_context': 'rawhide_compose_sync_to_mirrors',
        'product_version': 'fedora-rawhide',
        'subject': [{'productmd.compose.id': compose_id}],
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is False
    assert res_data['applicable_policies'] == ['openqa_important_stuff_for_rawhide']
    expected_summary = '1 of 2 required tests failed'
    assert res_data['summary'] == expected_summary
    expected_unsatisfied_requirements = [{
        u'item': {u'productmd.compose.id': compose_id},
        u'result_id': result['id'],
        u'testcase': testcase_name,
        u'type': u'test-result-failed',
        u'scenario': u'scenario2',
    }]
    assert res_data['unsatisfied_requirements'] == expected_unsatisfied_requirements


def test_ignore_waiver(requests_session, greenwave_server, testdatabuilder):
    """
    This tests that a waiver can be ignored when making the decision.
    """
    nvr = testdatabuilder.unique_nvr()
    result = testdatabuilder.create_result(item=nvr,
                                           testcase_name=all_rpmdiff_testcase_names[0],
                                           outcome='FAILED')
    waiver = testdatabuilder.create_waiver(result={
        "subject": dict([(key, value[0]) for key, value in result['data'].items()]),
        "testcase": all_rpmdiff_testcase_names[0]}, product_version='rhel-7')
    # The rest passed
    for testcase_name in all_rpmdiff_testcase_names[1:]:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r_ = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(data))
    assert r_.status_code == 200
    res_data = r_.json()
    assert res_data['policies_satisfied'] is True
    # Ignore the waiver
    data.update({
        'ignore_waiver': [waiver['id']]
    })
    r_ = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(data))
    assert r_.status_code == 200
    res_data = r_.json()
    expected_unsatisfied_requirements = [
        {
            'item': {'item': nvr, 'type': 'koji_build'},
            'result_id': result['id'],
            'testcase': all_rpmdiff_testcase_names[0],
            'type': 'test-result-failed',
            'scenario': None,
        },
    ]
    assert res_data['policies_satisfied'] is False
    assert res_data['unsatisfied_requirements'] == expected_unsatisfied_requirements


def test_cached_false_positive(requests_session, cached_greenwave_server, testdatabuilder):
    """ Test that caching without invalidation produces false positives.

    This just tests that our caching works in the first place.
    - Check a decision, it passes.
    - Insert a failing result.
    - Check the decision again, it passes

    (but it shouldn't) which means caching works.
    """
    nvr = testdatabuilder.unique_nvr()
    for testcase_name in all_rpmdiff_testcase_names:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'errata_newfile_to_qe',
        'product_version': 'rhel-7',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(cached_greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True

    # Now, insert a *failing* result.  The cache should return the old results
    # that exclude the failing one (erroneously).
    testdatabuilder.create_result(item=nvr,
                                  testcase_name=testcase_name,
                                  outcome='FAILED')
    r = requests_session.post(cached_greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    assert res_data['policies_satisfied'] is True


def test_blacklist(requests_session, greenwave_server, testdatabuilder):
    """
    Test that packages on the blacklist will be excluded when applying the policy.
    """
    nvr = 'firefox-1.0-1.el7'
    testdatabuilder.create_result(item=nvr,
                                  testcase_name=TASKTRON_RELEASE_CRITICAL_TASKS[0],
                                  outcome='FAILED')
    for testcase_name in TASKTRON_RELEASE_CRITICAL_TASKS[1:]:
        testdatabuilder.create_result(item=nvr,
                                      testcase_name=testcase_name,
                                      outcome='PASSED')
    data = {
        'decision_context': 'bodhi_update_push_stable',
        'product_version': 'fedora-26',
        'subject': [{'item': nvr, 'type': 'koji_build'}]
    }
    r = requests_session.post(greenwave_server.url + 'api/v1.0/decision',
                              headers={'Content-Type': 'application/json'},
                              data=json.dumps(data))
    assert r.status_code == 200
    res_data = r.json()
    # the failed test result of dist.abicheck should be ignored and thus the policy
    # is satisfied.
    assert res_data['policies_satisfied'] is True
