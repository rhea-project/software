## @ingroup Components-Energy-Networks
# Lift_Cruise.py
# 
# Created: Jan 2016, E. Botero
#          Mar 2020, M. Clarke
# Modified: 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import SUAVE

# package imports
import numpy as np
from SUAVE.Core import Units, Data
from SUAVE.Components.Propulsors.Propulsor import Propulsor

# ----------------------------------------------------------------------
#  Lift_Forward
# ----------------------------------------------------------------------

## @ingroup Components-Energy-Networks
class Lift_Cruise(Propulsor):
    """ This is a complex version of battery_propeller with a battery powering propellers through
        electric motors. In this case we have 2 sets of motors at different motors that can be controlled seperately
        
        This network adds 2 extra unknowns to the mission. The first is
        a voltage, to calculate the thevenin voltage drop in the pack.
        The second is torque matching between motor and propeller.
        
        We have two inputs, the forward throttle and the lift throttle setting
        Since this is an airplane first and foremost, the "throttle" will be for forward thrust
        The new unknown will be for lift throttle, because of the assumption on throttle something needs to be done...
        Want only 1 residual on voltage
    
        Assumptions:
        For any segment using this, body angle can't be an unknown.
        
        Source:
        None
    """        
    def __defaults__(self):
        """ This sets the default values for the network to function.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            N/A
        """             
        self.motor_lift                = None
        self.motor_forward             = None
        self.rotor            = None
        self.propeller         = None
        self.esc_lift                  = None
        self.esc_forward               = None
        self.avionics                  = None
        self.payload                   = None
        self.battery                   = None
        self.nacelle_diameter_lift     = None
        self.nacelle_diameter_forward  = None
        self.engine_length_lift        = None
        self.engine_length_forward     = None
        self.number_of_engines_lift    = None
        self.number_of_engines_forward = None
        self.voltage                   = None
        self.thrust_angle_lift         = 0.0
        self.thrust_angle_forward      = 0.0
        
        pass
        
    def evaluate_thrust(self,state):
        """ Calculate thrust given the current state of the vehicle
    
            Assumptions:
            Caps the throttle at 110% and linearly interpolates thrust off that
    
            Source:
            N/A
    
            Inputs:
            state [state()]
    
            Outputs:
            results.thrust_force_vector [Newtons]
            results.vehicle_mass_rate   [kg/s]
            conditions.propulsion:
                rpm_lift                 [radians/sec]
                rpm _forward             [radians/sec]
                current_lift             [amps]
                current_forward          [amps]
                battery_draw             [watts]
                battery_energy           [joules]
                voltage_open_circuit     [volts]
                voltage_under_load       [volts]
                motor_torque_lift        [N-M]
                motor_torque_forward     [N-M]
                propeller_torque_lift    [N-M]
                propeller_torque_forward [N-M]
    
            Properties Used:
            Defaulted values
        """          
        
        # unpack
        conditions        = state.conditions
        numerics          = state.numerics
        motor_lift        = self.motor_lift 
        motor_forward     = self.motor_forward
        rotor             = self.rotor 
        propeller         = self.propeller
        esc_lift          = self.esc_lift
        esc_forward       = self.esc_forward        
        avionics          = self.avionics
        payload           = self.payload
        battery           = self.battery
        num_lift          = self.number_of_engines_lift
        num_forward       = self.number_of_engines_forward
        
        #-----------------------------------------------------------------
        # SETUP BATTERIES AND ESC's
        #-----------------------------------------------------------------
        
        # Set battery energy
        battery.current_energy = conditions.propulsion.battery_energy    
        
        volts = state.unknowns.battery_voltage_under_load * 1. 
        volts[volts>self.voltage] = self.voltage 
        
        # ESC Voltage
        esc_lift.inputs.voltagein    = volts      
        esc_forward.inputs.voltagein = volts 
        
        #---------------------------------------------------------------
        # EVALUATE THRUST FROM FORWARD PROPULSORS 
        #---------------------------------------------------------------
        # Throttle the voltage
        esc_forward.voltageout(conditions) 
        
        # link
        motor_forward.inputs.voltage = esc_forward.outputs.voltageout
        
        # Run the motor
        motor_forward.omega(conditions)
        
        # link
        propeller.inputs.omega = motor_forward.outputs.omega
        propeller.thrust_angle = self.thrust_angle_forward   
        
        # Run the propeller
        F_forward, Q_forward, P_forward, Cp_forward, noise_forward, etap_forward = propeller.spin(conditions)
            
        # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
        eta = conditions.propulsion.throttle[:,0,None]
        P_forward[eta>1.0] = P_forward[eta>1.0]*eta[eta>1.0]
        F_forward[eta>1.0] = F_forward[eta>1.0]*eta[eta>1.0]        
        
        # Run the motor for current
        i, etam_forward = motor_forward.current(conditions)  
        
        # Fix the current for the throttle cap
        motor_forward.outputs.current[eta>1.0] = motor_forward.outputs.current[eta>1.0]*eta[eta>1.0]
        
        # link
        esc_forward.inputs.currentout =  motor_forward.outputs.current 
        
        # Run the esc
        esc_forward.currentin(conditions)        
       
        #-------------------------------------------------------------------
        # EVALUATE THRUST FROM LIFT PROPULSORS 
        #-------------------------------------------------------------------
        
        # Make a new set of konditions, since there are differences for the esc and motor
        konditions                                        = Data()
        konditions.propulsion                             = Data()
        konditions.freestream                             = Data()
        konditions.frames                                 = Data()
        konditions.frames.inertial                        = Data()
        konditions.frames.body                            = Data()
        konditions.propulsion.acoustic_outputs            = Data()                
        konditions.propulsion.throttle                    = conditions.propulsion.throttle_lift* 1.
        konditions.propulsion.propeller_power_coefficient = conditions.propulsion.propeller_power_coefficient_lift * 1.
        konditions.freestream.density                     = conditions.freestream.density * 1.
        konditions.freestream.velocity                    = conditions.freestream.velocity * 1.
        konditions.freestream.dynamic_viscosity           = conditions.freestream.dynamic_viscosity * 1.
        konditions.freestream.speed_of_sound              = conditions.freestream.speed_of_sound *1.
        konditions.freestream.temperature                 = conditions.freestream.temperature * 1.
        konditions.freestream.altitude                    = conditions.freestream.altitude * 1.
        konditions.frames.inertial.velocity_vector        = conditions.frames.inertial.velocity_vector *1.
        konditions.frames.body.transform_to_inertial      = conditions.frames.body.transform_to_inertial

        # Throttle the voltage
        esc_lift.voltageout(konditions)       
        # link
        motor_lift.inputs.voltage = esc_lift.outputs.voltageout
        
        # Run the motor
        motor_lift.omega(konditions)
        # link
        rotor.inputs.omega = motor_lift.outputs.omega
        rotor.thrust_angle = self.thrust_angle_lift
        
        # Run the propeller
        F_lift, Q_lift, P_lift, Cp_lift, output_lift, etap_lift = rotor.spin(konditions)
            
        # Check to see if magic thrust is needed, the ESC caps throttle at 1.1 already
        eta = state.conditions.propulsion.throttle_lift
        P_lift[eta>1.0] = P_lift[eta>1.0]*eta[eta>1.0]
        F_lift[eta>1.0] = F_lift[eta>1.0]*eta[eta>1.0]        
        
        # Run the motor for current
        i, etam_lift = motor_lift.current(konditions)  
        
        # Fix the current for the throttle cap
        motor_lift.outputs.current[eta>1.0] = motor_lift.outputs.current[eta>1.0]*eta[eta>1.0]
        
        # link
        esc_lift.inputs.currentout =  motor_lift.outputs.current     
        
        # Run the esc
        esc_lift.currentin(konditions)          
        
        ##
        # COMBINE THRUST AND POWER
        ##
        
        # Run the avionics
        avionics.power()
    
        # Run the payload
        payload.power()
        
        # Calculate avionics and payload power
        avionics_payload_power = avionics.outputs.power + payload.outputs.power
    
        # Calculate avionics and payload current
        i_avionics_payload = avionics_payload_power/volts   
        
        # Add up the power usages
        i_lift    = esc_lift.outputs.currentin*num_lift 
        i_forward = esc_forward.outputs.currentin*num_forward
        
        current_total = i_lift + i_forward + i_avionics_payload
        power_total   = current_total * volts   
        
        battery.inputs.current  = current_total
        battery.inputs.power_in = - power_total
        
        # Run the battery
        battery.energy_calc(numerics)   
        
        # Pack the conditions
        a                    = conditions.freestream.speed_of_sound
        R_lift               = rotor.tip_radius
        R_forward            = propeller.tip_radius
        rpm_lift             = motor_lift.outputs.omega / Units.rpm
        rpm_forward          = motor_forward.outputs.omega / Units.rpm 
        battery_draw         = battery.inputs.power_in 
        battery_energy       = battery.current_energy 
        voltage_open_circuit = battery.voltage_open_circuit
        voltage_under_load   = battery.voltage_under_load    
        
        conditions.propulsion.acoustic_outputs[propeller.tag] = noise_forward
        conditions.propulsion.acoustic_outputs[rotor.tag]     = output_lift
    
        conditions.propulsion.rpm_lift                          = rpm_lift
        conditions.propulsion.current_lift                      = i_lift 
        conditions.propulsion.motor_torque_lift                 = motor_lift.outputs.torque
        conditions.propulsion.motor_torque_forward              = motor_forward.outputs.torque
        conditions.propulsion.motor_efficiency_lift             = etam_lift           
        conditions.propulsion.propeller_torque_lift             = Q_lift 
        conditions.propulsion.propeller_tip_mach_lift           = (motor_lift.outputs.omega * R_lift )/a
        conditions.propulsion.propeller_efficiency_lift         = etap_lift
        conditions.propulsion.propeller_power_lift              = P_lift*num_lift
        conditions.propulsion.propeller_thrust_lift             = F_lift*num_lift        
        conditions.propulsion.propeller_power_coefficient_lift  = Cp_lift        
        conditions.propulsion.propeller_thrust_coefficient_lift = output_lift.thrust_coefficient  
        conditions.propulsion.battery_draw_lift                 = -i_lift * volts 

        conditions.propulsion.rpm_forward                       = rpm_forward        
        conditions.propulsion.battery_draw                      = battery_draw
        conditions.propulsion.battery_draw_forward              = -i_forward * volts 
        conditions.propulsion.battery_energy                    = battery_energy
        conditions.propulsion.voltage_open_circuit              = voltage_open_circuit
        conditions.propulsion.voltage_under_load                = voltage_under_load   
        conditions.propulsion.motor_efficiency_forward          = etam_forward
        conditions.propulsion.current_forward                   = i_forward 
        conditions.propulsion.battery_efficiency                = (battery_draw+battery.resistive_losses)/battery_draw
        conditions.propulsion.payload_efficiency                = (battery_draw+(avionics.outputs.power + payload.outputs.power))/battery_draw            
        conditions.propulsion.propeller_power_forward           = P_forward*num_forward
        conditions.propulsion.propeller_thrust_coefficient      = Cp_forward 
        conditions.propulsion.propeller_tip_mach_forward        = (motor_forward.outputs.omega * R_forward)/a
        conditions.propulsion.propeller_torque_forward          = Q_forward       
        conditions.propulsion.propeller_efficiency_forward      = etap_forward 
        conditions.propulsion.current                           = i_lift + i_forward 
        conditions.propulsion.battery_specfic_power             = -battery_draw/battery.mass_properties.mass    # kWh/kg
        conditions.propulsion.electronics_efficiency            = -(P_forward*num_forward+P_lift*num_lift)/battery_draw  
        conditions.propulsion.battery_current                   = current_total
        
        # Calculate the thrust and mdot
        F_lift_total    = F_lift*num_lift * [np.cos(self.thrust_angle_lift),0,-np.sin(self.thrust_angle_lift)]    
        F_forward_total = F_forward*num_forward * [np.cos(self.thrust_angle_forward),0,-np.sin(self.thrust_angle_forward)] 


        F_lift_mag = np.atleast_2d(np.linalg.norm(F_lift_total, axis=1)/Units.lbs ) # lb 
        F_forward_mag =  np.atleast_2d(np.linalg.norm(F_forward_total, axis=1)/Units.lbs) # lb   
        
        conditions.propulsion.disc_loading_lift                 = (F_lift_mag.T)/(self.number_of_engines_lift*np.pi*(R_lift /Units.feet)**2) # lb/ft^2      
        conditions.propulsion.disc_loading_forward              = (F_forward_mag.T)/(self.number_of_engines_forward*np.pi*(R_forward/Units.feet)**2) # lb/ft^2       
        conditions.propulsion.power_loading_lift                = (F_lift_mag.T)/(battery_draw/Units.hp)            # lb/hp         
        conditions.propulsion.power_loading_forward             = (F_forward_mag.T)/(battery_draw/Units.hp)         # lb/hp 
        
        F_total = F_lift_total + F_forward_total
        mdot    = np.zeros_like(F_total)
        
        results = Data()
        results.thrust_force_vector = F_total
        results.vehicle_mass_rate   = mdot    
        
        return results
    
    def unpack_unknowns_transition(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses all the motors.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient_lift[None]
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift               [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient_lift [None]
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift              [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """          
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.battery_voltage_under_load        = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.propeller_power_coefficient_lift  = segment.state.unknowns.propeller_power_coefficient_lift
        segment.state.conditions.propulsion.propeller_power_coefficient       = segment.state.unknowns.propeller_power_coefficient   
        segment.state.conditions.propulsion.throttle_lift                     = segment.state.unknowns.throttle_lift        
        segment.state.conditions.propulsion.throttle                          = segment.state.unknowns.throttle
        
        return
    
    
    def unpack_unknowns_no_lift(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the forward motors and turns the rest off.
    
            Assumptions:
            Only the forward motors and turns the rest off.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift              [0-1]
            state.unknowns.throttle                    [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift              [0-1]
            state.conditions.propulsion.throttle                    [0-1]
    
            Properties Used:
            N/A
        """             
        
        ones = segment.state.ones_row
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.throttle_lift                       = 0.0 * ones(1)
        segment.state.conditions.propulsion.battery_voltage_under_load          = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.propeller_power_coefficient         = segment.state.unknowns.propeller_power_coefficient
        segment.state.conditions.propulsion.propeller_power_coefficient_lift    = 0.0 * ones(1)
        segment.state.conditions.propulsion.throttle                            = segment.state.unknowns.throttle
        
        return    
    
    def unpack_unknowns_no_forward(self,segment):
        """ This is an extra set of unknowns which are unpacked from the mission solver and send to the network.
            This uses only the lift motors.
    
            Assumptions:
            Only the lift motors.
    
            Source:
            N/A
    
            Inputs:
            state.unknowns.propeller_power_coefficient [None]
            state.unknowns.battery_voltage_under_load  [volts]
            state.unknowns.throttle_lift              [0-1]
            state.unknowns.throttle            [0-1]
    
            Outputs:
            state.conditions.propulsion.propeller_power_coefficient [None]
            state.conditions.propulsion.battery_voltage_under_load  [volts]
            state.conditions.propulsion.throttle_lift              [0-1]
            state.conditions.propulsion.throttle            [0-1]
    
            Properties Used:
            N/A
        """             
        
        ones = segment.state.ones_row
        
        # Here we are going to unpack the unknowns (Cps,throttle,voltage) provided for this network
        segment.state.conditions.propulsion.throttle_lift                        = segment.state.unknowns.throttle_lift
        segment.state.conditions.propulsion.battery_voltage_under_load           = segment.state.unknowns.battery_voltage_under_load
        segment.state.conditions.propulsion.propeller_power_coefficient          = 0.0 * ones(1)
        segment.state.conditions.propulsion.propeller_power_coefficient_lift     = segment.state.unknowns.propeller_power_coefficient_lift
        segment.state.conditions.propulsion.throttle                             = 0.0 * ones(1)
        
        return    
    
    def residuals_transition(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if all motors are operational
    
            Assumptions:
            All motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                motor_torque_forward                  [N-m]
                motor_torque_lift                     [N-m]
                propeller_torque_forward              [N-m]
                propeller_torque_lift                 [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """            
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_motor_forward = segment.state.conditions.propulsion.motor_torque_forward
        q_prop_forward  = segment.state.conditions.propulsion.propeller_torque_forward
        q_motor_lift    = segment.state.conditions.propulsion.motor_torque_lift
        q_prop_lift     = segment.state.conditions.propulsion.propeller_torque_lift        
        
        v_actual        = segment.state.conditions.propulsion.voltage_under_load
        v_predict       = segment.state.unknowns.battery_voltage_under_load
        v_max           = self.voltage        
        
        # Return the residuals
        segment.state.residuals.network[:,0] = (q_motor_forward[:,0] - q_prop_forward[:,0])/q_motor_forward[:,0] 
        segment.state.residuals.network[:,1] = (q_motor_lift[:,0] - q_prop_lift[:,0])/q_motor_lift[:,0]
        segment.state.residuals.network[:,2] = (v_predict[:,0] - v_actual[:,0])/v_max  

        return
    
    
    def residuals_no_lift(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Use this if only the forward motors are operational
    
            Assumptions:
            Only the forward motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                motor_torque_forward                  [N-m]
                motor_torque_lift                     [N-m]
                propeller_torque_forward              [N-m]
                propeller_torque_lift                 [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
            
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """          
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_motor_forward = segment.state.conditions.propulsion.motor_torque_forward
        q_prop_forward  = segment.state.conditions.propulsion.propeller_torque_forward   
        
        v_actual        = segment.state.conditions.propulsion.voltage_under_load
        v_predict       = segment.state.unknowns.battery_voltage_under_load
        v_max           = self.voltage        
        
        # Return the residuals
        segment.state.residuals.network[:,0] = q_motor_forward[:,0] - q_prop_forward[:,0]
        segment.state.residuals.network[:,1] = (v_predict[:,0] - v_actual[:,0])/v_max 
        return    
    
    def residuals_no_forward(self,segment):
        """ This packs the residuals to be send to the mission solver.
            Only the lift motors are operational
    
            Assumptions:
            The lift motors are operational
    
            Source:
            N/A
    
            Inputs:
            state.conditions.propulsion:
                motor_torque_forward                  [N-m]
                motor_torque_lift                     [N-m]
                propeller_torque_forward              [N-m]
                propeller_torque_lift                 [N-m]
                voltage_under_load                    [volts]
            state.unknowns.battery_voltage_under_load [volts]
    
            Outputs:
            None
    
            Properties Used:
            self.voltage                              [volts]
        """            
        
        # Here we are going to pack the residuals (torque,voltage) from the network
        q_motor_lift    = segment.state.conditions.propulsion.motor_torque_lift
        q_prop_lift     = segment.state.conditions.propulsion.propeller_torque_lift        

        v_actual        = segment.state.conditions.propulsion.voltage_under_load
        v_predict       = segment.state.unknowns.battery_voltage_under_load
        v_max           = self.voltage        
        
        # Return the residuals
        segment.state.residuals.network[:,0] = (q_motor_lift[:,0] - q_prop_lift[:,0])/q_motor_lift[:,0]
        segment.state.residuals.network[:,1] = (v_predict[:,0] - v_actual[:,0])/v_max  
        return