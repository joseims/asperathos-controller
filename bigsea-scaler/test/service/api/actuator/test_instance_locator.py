# Copyright (c) 2017 LSD - UFCG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from service.api.actuator.plugins.instance_locator import Instance_Locator
from utils.ssh_utils import SSH_Utils
from mock.mock import MagicMock


class Test_Instance_Locator(unittest.TestCase):

    def setUp(self):
        self.compute_1 = "compute1"
        self.compute_2 = "compute2"
        self.user = "root"
        self.vm_id = "vm-id"
        
        self.ssh_utils = SSH_Utils({})
        self.compute_nodes = [self.compute_1, self.compute_2]
        self.compute_nodes_key = "key"
        self.instance_locator = Instance_Locator(self.ssh_utils, self.compute_nodes, self.compute_nodes_key)

    def tearDown(self):
        pass

    def located(self, command, user, host, key):
        return {self.compute_1:"0\n", self.compute_2:"1\n"}[host]

    def impossible_to_locate(self, command, user, host, key):
        return {self.compute_1:"1\n", self.compute_2:"1\n"}[host]

    def test_locate(self):
        self.ssh_utils.run_and_get_result = MagicMock()
        self.ssh_utils.run_and_get_result.side_effect = self.located
        
        result = self.instance_locator.locate(self.vm_id)
        
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), 
                                                          self.user, self.compute_1, self.compute_nodes_key)
        self.assertEquals(result, self.compute_1)
        
    def test_locate_impossible_to_find_instance(self):
        self.ssh_utils.run_and_get_result = MagicMock()
        self.ssh_utils.run_and_get_result.side_effect = self.impossible_to_locate
        
        self.assertRaises(Exception, self.instance_locator.locate, self.vm_id)
        
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), self.user, 
                                                          self.compute_1, self.compute_nodes_key)
        self.ssh_utils.run_and_get_result.assert_any_call("virsh schedinfo %s > /dev/null 2> /dev/null ; echo $?" % (self.vm_id), self.user, 
                                                          self.compute_2, self.compute_nodes_key)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()