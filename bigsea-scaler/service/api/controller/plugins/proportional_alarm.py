from utils.logger import Log, configure_logging
import datetime

class Proportional_Alarm:

    ERROR_METRIC_NAME = "application-progress.error"

    def __init__(self, actuator, metric_source, trigger_down, trigger_up, min_cap, max_cap, metric_rounding):
        # TODO: Check parameters
        self.metric_source = metric_source
        self.actuator = actuator
        self.trigger_down = trigger_down
        self.trigger_up = trigger_up
        self.min_cap = min_cap
        self.max_cap = max_cap
        self.metric_rounding = metric_rounding

        self.logger = Log("proportional.alarm.log", "scaler.log")
        configure_logging()
        
        self.last_progress_error_timestamp = datetime.datetime.strptime("0001-01-01T00:00:00.0Z", '%Y-%m-%dT%H:%M:%S.%fZ')
        self.last_progress_error = None

    def check_application_state(self, application_id, instances):
        """
            Checks the application progress by getting progress metrics from a 
            metric source, checks if the metrics are new and tries to modify the
            amount of allocated resources if necessary.
        """
        
        # TODO: Check parameters
        try:
            self.logger.log("Getting progress error")
            # Get the progress error value and timestamp

            progress_error_timestamp, progress_error = self._get_progress_error(application_id)
            self.logger.log("Progress error-[%s]-%f" % (str(progress_error_timestamp), progress_error))

            # Check if the metric is new by comparing the timestamps of the current metric and most recent metric
            if self._check_measurements_are_new(progress_error_timestamp):
                self._scale(progress_error, instances)
                
                self.last_progress_error = progress_error
                self.last_progress_error_timestamp = progress_error_timestamp
            else:
                self.logger.log("Could not acquire more recent metrics")
        except Exception:
            # TODO: Check exception type
            self.logger.log("Could not get metrics")
            return

    def _scale(self, progress_error, instances):
        if self.last_progress_error != None:
            difference = progress_error - self.last_progress_error
        else:
            difference = 0.0
        
        # If the error is positive and its absolute value is too high, scale down
        if progress_error > 0 and progress_error >= self.trigger_down:
            self.logger.log("Scaling down")
            
            # Get current CPU cap
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = max(cap - self.actuation_size, self.min_cap)
            
            # Currently, we use the same cap for all the vms
            cap_instances = {instance:new_cap for instance in instances}
            
            # Set the new cap
            self.actuator.adjust_resources(cap_instances)
        # If the error is negative and its absolute value is too high, scale up
        elif progress_error < 0 and abs(progress_error) >= self.trigger_up:
            self.logger.log("Scaling up")
            
            # Get current CPU cap
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = min(cap + self.actuation_size, self.max_cap)
            
            # Currently, we use the same cap for all the vms
            cap_instances = {instance:new_cap for instance in instances}
    
            # Set the new cap
            self.actuator.adjust_resources(cap_instances)
        else:   
            if difference < 0.0:
                cap = self.actuator.get_allocated_resources(instances[0])
                new_cap = min(cap + abs(difference), self.max_cap)
                
                cap_instances = {instance:new_cap for instance in instances}
                self.actuator.adjust_resources(cap_instances)
            elif difference > 0.0:
                cap = self.actuator.get_allocated_resources(instances[0])
                new_cap = max(cap - abs(difference), self.min_cap)
                
                cap_instances = {instance:new_cap for instance in instances}
                self.actuator.adjust_resources(cap_instances)
        

    def _scale_down(self, progress_error, instances):
        """
            Checks if it is necessary to scale down, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """
        
        # If the error is positive and its absolute value is too high, scale down
        if progress_error > 0 and progress_error >= self.trigger_down:
            self.logger.log("Scaling down")
            
            # Get current CPU cap
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = max(cap - self.actuation_size, self.min_cap)
            
            # Currently, we use the same cap for all the vms
            cap_instances = {instance:new_cap for instance in instances}
            
            # Set the new cap
            self.actuator.adjust_resources(cap_instances)
            
    def _scale_up(self, progress_error, instances):
        """
            Checks if it is necessary to scale up, according to
            the progress_error. If it is, calculates the new CPU cap
            value and tries to modify the cap of the vms.
        """
        
        # If the error is negative and its absolute value is too high, scale up
        if progress_error < 0 and abs(progress_error) >= self.trigger_up:
            self.logger.log("Scaling up")
            
            # Get current CPU cap
            cap = self.actuator.get_allocated_resources(instances[0])
            new_cap = min(cap + self.actuation_size, self.max_cap)
            
            # Currently, we use the same cap for all the vms
            cap_instances = {instance:new_cap for instance in instances}
    
            # Set the new cap
            self.actuator.adjust_resources(cap_instances)
    
    def _get_progress_error(self, application_id):
        progress_error_measurement = self.metric_source.get_most_recent_value(Proportional_Alarm.ERROR_METRIC_NAME,
                                                                {"application_id":application_id})
        progress_error_timestamp = progress_error_measurement[0]
        progress_error = progress_error_measurement[1]
        progress_error = round(progress_error, self.metric_rounding)
        return progress_error_timestamp, progress_error

    def _check_measurements_are_new(self, progress_error_timestamp):
        return self.last_progress_error_timestamp < progress_error_timestamp