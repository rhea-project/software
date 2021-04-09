## @ingroup Methods-Missions-Segments-Descent
# Constant_mach_Constant_Rate.py
# 
# Created:  Aug 2020, S. Karpuk
# Modified: 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
import SUAVE

# ----------------------------------------------------------------------
#  Initialize Conditions
# ----------------------------------------------------------------------

## @ingroup Methods-Missions-Segments-Descent
def initialize_conditions(segment):
    """Sets the specified conditions which are given for the segment type.

    Assumptions:
    Constant speed and constant descent rate

    Source:
    N/A

    Inputs:
    segment.descent_rate                                [meters/second]
    segment.altitude_start                              [meters]
    segment.altitude_end                                [meters]
    segment.air_speed                                   [meters/second]
    segment.state.numerics.dimensionless.control_points [array]

    Outputs:
    conditions.frames.inertial.velocity_vector  [meters/second]
    conditions.frames.inertial.position_vector  [meters]
    conditions.freestream.altitude              [meters]
    conditions.frames.inertial.time             [seconds]

    Properties Used:
    N/A
    """     
    
    # unpack
    descent_rate = segment.descent_rate
    mach_number  = segment.mach   
    alt0         = segment.altitude_start 
    altf         = segment.altitude_end
    t_nondim     = segment.state.numerics.dimensionless.control_points
    conditions   = segment.state.conditions  

    # check for initial altitude
    if alt0 is None:
        if not segment.state.initials: raise AttributeError('initial altitude not set')
        alt0 = -1.0 *segment.state.initials.conditions.frames.inertial.position_vector[-1,2]

    # discretize on altitude
    alt = t_nondim * (altf-alt0) + alt0
    conditions.freestream.altitude[:,0]             =  alt[:,0] # positive altitude in this context

     # Update freestream to get speed of sound
    SUAVE.Methods.Missions.Segments.Common.Aerodynamics.update_atmosphere(segment)
    a = conditions.freestream.speed_of_sound   

    # process velocity vector
    v_mag = mach_number * a
    v_z   = descent_rate # z points down
    v_x   = np.sqrt( v_mag**2 - v_z**2 )
    
    # pack conditions    
    conditions.frames.inertial.velocity_vector[:,0] = v_x[:,0]
    conditions.frames.inertial.velocity_vector[:,2] = v_z
    conditions.frames.inertial.position_vector[:,2] = -alt[:,0] # z points down
    conditions.freestream.altitude[:,0]             =  alt[:,0] # positive altitude in this context