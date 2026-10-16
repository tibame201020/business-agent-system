import unittest
from flake_audit import analyze,gather
class TestAudit(unittest.TestCase):
 def test_correlated_rerun_not_overclaimed(self):
  runs=[{"id":11,"name":"CI","conclusion":"success","run_attempt":2,"head_sha":"a"*40,"html_url":"https://github.com/acme/ci/actions/runs/11"},{"id":12,"conclusion":"failure","run_attempt":2}]
  def jobs(id,attempt):return ([{"name":"build","conclusion":"failure"},{"name":"unit","conclusion":"success"}] if attempt==1 else [{"name":"build","conclusion":"success"}])
  rows=analyze(runs,jobs)
  self.assertEqual(len(rows),1);self.assertTrue(rows[0]["latest_attempt_same_job_passed"]);self.assertEqual(rows[0]["classification"],"RETRY_CORRELATED_UNVERIFIED_CAUSE")
 def test_no_false_failure_when_retry_did_not_pass_job(self):
  rows=analyze([{"id":1,"name":"CI","conclusion":"success","run_attempt":2}],lambda id,n:[{"name":"unit" if n==1 else "deploy","conclusion":"failure" if n==1 else "success"}])
  self.assertFalse(rows[0]["latest_attempt_same_job_passed"])
 def test_single_attempt_has_no_findings(self):
  self.assertEqual(analyze([{"id":1,"conclusion":"success","run_attempt":1}],lambda *a:[]),[])
 def test_repository_input_contract(self):
  with self.assertRaises(ValueError):gather("../local")
if __name__=="__main__":unittest.main()
