#!/usr/bin/env python3

import rospy 
from smach import State, StateMachine
from time import sleep 
from std_msgs.msg import Int32
from std_msgs.msg import Int32MultiArray 

'''
3 different state for robot.
    1- Charge
    2- Navigate to goal
    3- Wait for command
'''
class Charge(State):
    def __init__(self):
        State.__init__( self, 
                        outcomes=['charge', 'wait'], 
                        input_keys=['battery_percentage'],
                        output_keys=['battery_percentage'])

    def execute(self, ud):
        sleep(2)
        if ud.battery_percentage < 50:
            rospy.loginfo('Executing state Charge')
            rospy.loginfo(ud.battery_percentage)
            ud.battery_percentage += 10
            return 'charge'
        else:
            rospy.loginfo('Executing state Wait')
            return 'wait'

class Navigate(State):

    def __init__(self):
        State.__init__( self, 
                        outcomes=['navigate', 'wait'],
                        input_keys=['goal_location', 'current_location'],
                        output_keys=['goal_location'])
    
    def execute(self, ud):
        sleep(2)
        if ud.goal_location != ud.current_location:
            rospy.loginfo('Navigating to goal location')
            sleep(5)
            ud.goal_location = ud.current_location
            return 'navigate'
        else:
            rospy.loginfo('Executing state Wait')
            return 'wait'

class Wait(State):

   
    def to_charge(self, data):
        rospy.loginfo('to_charge')
        self.battery_percentage = data.data
        data.data = 50
        self.mission = 'charge'

    def to_navigate(self, data):
        rospy.loginfo('to_navigate')
        self.goal_location = data.data
        self.mission = 'navigate'
        self.flag = True
        

            

    def __init__(self):
        State.__init__( self, 
                        outcomes=['navigate', 'charge', 'wait'],
                        output_keys=['goal_location', 'battery_percentage', 'current_location'])
        self.subscriber = rospy.Subscriber('/battery_percentage', Int32, self.to_charge)
        self.subscriber = rospy.Subscriber('/navigate', Int32MultiArray, self.to_navigate)
        self.mission = False
        self.flag = True

        
        
    def execute(self, ud):

        sleep(2)
        if self.mission == 'navigate' and self.flag:
            self.flag = False
            ud.goal_location = self.goal_location
            return 'navigate'
        elif self.mission == 'charge':
            ud.battery_percentage = self.battery_percentage
            return 'charge'
        else:
            return 'wait'
        




def main():
    rospy.init_node('smach_example_state_machine')
    sm = StateMachine(outcomes=['charge', 'navigate', 'wait'])

    sm.userdata.battery_percentage = 25

    with sm:
        StateMachine.add('Charge', Charge(), 
                               transitions={'charge':'Charge', 
                                            'wait':'Wait'})
        StateMachine.add('Navigate', Navigate(), 
                               transitions={'navigate':'Navigate', 
                                            'wait':'Wait'})
        StateMachine.add('Wait', Wait(), 
                               transitions={'navigate':'Navigate', 
                                            'charge':'Charge',
                                            'wait':'Wait'})
                    

    outcome = sm.execute()

if __name__=='__main__':
    main()


