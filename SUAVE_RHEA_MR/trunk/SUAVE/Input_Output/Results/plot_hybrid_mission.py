## @ingroup Input_Output-Results
# plot_my_mission.py

# Created:  Stanislav Karpuk
# Modified: 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
import numpy as np
import pylab as plt

from SUAVE.Core import Units
import time                     # importing library
import datetime                 # importing library

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------
## @ingroup Input_Output-Results
def plot_hybrid_mission(case_name,results,x_axes='range', line_style='bo-'):

    axis_font = {'fontname':'Arial', 'size':'14'}    

    # ------------------------------------------------------------------
    #   Aerodynamics
    # ------------------------------------------------------------------

#    x_axes = 'range'
    fig = plt.figure("Aerodynamic Forces",figsize=(8,6))

    for segment in results.segments.values():


        time      = segment.conditions.frames.inertial.time[:,0] / Units.min
        Thrust    = segment.conditions.frames.body.thrust_force_vector[:,0]/1000 #             in kN # / Units.lbf
        Thrust_EM = segment.conditions.propulsion.thrust_breakdown.electric[:,0]/1000 
        Thrust_GT = segment.conditions.propulsion.thrust_breakdown.jet[:,0]/1000 
        mdot      = segment.conditions.weights.vehicle_mass_rate[:,0]
        thrust    =  segment.conditions.frames.body.thrust_force_vector[:,0]
        sfc       = mdot/thrust*100000 # in e-5 kg/N/s #(mdot / Units.lb) / (thrust /Units.lbf) * Units.hr
        eta       = segment.conditions.propulsion.throttle[:,0]
        Dist      = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
        if x_axes == 'range':
            axes = fig.add_subplot(2,1,1)
            axes.plot( Dist , Thrust , 'ro-')
            axes.plot( Dist , Thrust_EM , 'go-')
            axes.plot( Dist , Thrust_GT , line_style)
            axes.set_ylabel('Thrust (kN)',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(2,1,2)
            axes.plot( Dist , eta , line_style )
            axes.set_xlabel('Range (NM)',axis_font)
            axes.set_ylabel('Throttle',axis_font)
            axes.grid(True)

#            axes = fig.add_subplot(2,1,2)
#            axes.plot( Dist , sfc , line_style )
#            axes.set_xlabel('Range (NM)',axis_font)
#            axes.set_ylabel('sfc (10-5 kg/N/s)',axis_font)
##            axes.set_ylabel('sfc (lb/lbf-hr)',axis_font)
#            axes.grid(True)

            
            #plt.savefig(case_name + "_engine_R.pdf")
            plt.savefig(case_name + "_engine_R.png")
        else:
            axes = fig.add_subplot(2,1,1)
            axes.plot( time , Thrust , line_style, label='Total' )
            axes.plot( time , Thrust_EM , line_style, label='Electric' )
            axes.plot( time , Thrust_GT , line_style, label='Gas-turbine'  )
            axes.set_ylabel('Thrust (kN)',axis_font)
            axes.grid(True)
            axes.legend()

            axes = fig.add_subplot(2,1,2)
            axes.plot( Dist , eta , line_style )
            axes.set_xlabel('Time (min)',axis_font)
            axes.set_ylabel('Throttle',axis_font)
            axes.grid(True)


#            axes = fig.add_subplot(2,1,2)
#            axes.plot( time , sfc , line_style )
#            axes.set_xlabel('Time (min)',axis_font)
#            axes.set_ylabel('sfc (10-5 kg/N/s)',axis_font)
#            axes.grid(True)
            
            
            
            
            
            #plt.savefig(case_name + "_engine_t.pdf")
            plt.savefig(case_name + "_engine_t.png")
#        plt.savefig("LR_newDesign_engine.pdf")
#        plt.savefig("LR_newDesign_engine.png")

    # ------------------------------------------------------------------
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Coefficients",figsize=(8,10))
    for segment in results.segments.values():

        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
        CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
        aoa = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        l_d = CLift/CDrag
        Dist = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
        if x_axes == 'range':
            axes = fig.add_subplot(3,1,1)
            axes.plot( Dist , CLift , line_style )
            axes.set_ylabel('Lift Coefficient',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,2)
            axes.plot( Dist , l_d , line_style )
            axes.set_ylabel('L/D',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,3)
            axes.plot( Dist , aoa , 'ro-' )
            axes.set_xlabel('Range (NM)',axis_font)
            axes.set_ylabel('AOA (deg)',axis_font)
            axes.grid(True)
            #plt.savefig(case_name + "_aero_R.pdf")
            plt.savefig(case_name + "_aero_R.png")            
        else:
            axes = fig.add_subplot(3,1,1)
            axes.plot( time , CLift , line_style )
            axes.set_ylabel('Lift Coefficient',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,2)
            axes.plot( time , l_d , line_style )
            axes.set_ylabel('L/D',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,3)
            axes.plot( time , aoa , 'ro-' )
            axes.set_xlabel('Time (min)',axis_font)
            axes.set_ylabel('AOA (deg)',axis_font)
            axes.grid(True)
            #plt.savefig(case_name + "_aero_t.pdf")
            plt.savefig(case_name + "_aero_t.png")               
#        plt.savefig("LR_newDesign_aero.pdf")
#        plt.savefig("LR_newDesign_aero.png")

    # ------------------------------------------------------------------
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Drag Components",figsize=(8,10))
    axes = plt.gca()
    for i, segment in enumerate(results.segments.values()):

        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        drag_breakdown = segment.conditions.aerodynamics.drag_breakdown
        cdp = drag_breakdown.parasite.total[:,0]
        cdi = drag_breakdown.induced.total[:,0]
        cdc = drag_breakdown.compressible.total[:,0]
        cdm = drag_breakdown.miscellaneous.total[:,0]
        cd  = drag_breakdown.total[:,0]
        Dist = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
        if x_axes == 'range':
            if line_style == 'bo-':
                axes.plot( Dist , cdp , 'ko-', label='CD parasite' )
                axes.plot( Dist , cdi , 'bo-', label='CD induced' )
                axes.plot( Dist , cdc , 'go-', label='CD compressibility' )
                axes.plot( Dist , cdm , 'yo-', label='CD miscellaneous' )
                axes.plot( Dist , cd  , 'ro-', label='CD total'   )
                if i == 0:
                        axes.legend(loc='upper center')                
            else:
                axes.plot( Dist , cdp , line_style )
                axes.plot( Dist , cdi , line_style )
                axes.plot( Dist , cdc , line_style )
                axes.plot( Dist , cdm , line_style )
                axes.plot( Dist , cd  , line_style ) 
            axes.set_xlabel('Range (NM)')                
            axes.set_ylabel('CD')
            axes.grid(True)
            #plt.savefig(case_name + "_drag_R.pdf")
            plt.savefig(case_name + "_drag_R.png")               
        else:
            if line_style == 'bo-':
                axes.plot( time , cdp , 'ko-', label='CD parasite' )
                axes.plot( time , cdi , 'bo-', label='CD induced' )
                axes.plot( time , cdc , 'go-', label='CD compressibility' )
                axes.plot( time , cdm , 'yo-', label='CD miscellaneous' )
                axes.plot( time , cd  , 'ro-', label='CD total'   )
                if i == 0:
                        axes.legend(loc='upper center')                
            else:
                axes.plot( time , cdp , line_style )
                axes.plot( time , cdi , line_style )
                axes.plot( time , cdc , line_style )
                axes.plot( time , cdm , line_style )
                axes.plot( time , cd  , line_style )            
            axes.set_xlabel('Time (min)')
            axes.set_ylabel('CD')
            axes.grid(True)
            #plt.savefig(case_name + "_newDesign_drag_t.pdf")
            plt.savefig(case_name + "_newDesign_drag_t.png")            
            
#    axes.set_ylabel('CD')
#    axes.grid(True)
#    plt.savefig("LR_newDesign_drag_R.pdf")
#    plt.savefig("LR_newDesign_drag_R.png")

    # ------------------------------------------------------------------
    #   Altitude, sfc, vehicle weight
    # ------------------------------------------------------------------

    fig = plt.figure("Altitude_sfc_weight",figsize=(8,10))
    for segment in results.segments.values():

        time     = segment.conditions.frames.inertial.time[:,0] / Units.min
        aoa      = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        mass     = segment.conditions.weights.total_mass[:,0]# / Units.lb
        altitude = segment.conditions.freestream.altitude[:,0] / Units.ft
        mdot     = segment.conditions.weights.vehicle_mass_rate[:,0]
        thrust   =  segment.conditions.frames.body.thrust_force_vector[:,0]
        sfc      = (mdot / Units.lb) / (thrust /Units.lbf) * Units.hr
        Dist = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
        if x_axes == 'range':
            axes = fig.add_subplot(2,1,1)
            axes.plot( Dist , altitude , line_style )
            axes.set_ylabel('Altitude (ft)',axis_font)
            axes.grid(True)

#            axes = fig.add_subplot(3,1,3)
#            axes.plot( Dist , sfc , line_style )
#            axes.set_xlabel('Range (NM)',axis_font)
#            axes.set_ylabel('sfc (lb/lbf-hr)',axis_font)
#            axes.grid(True)

            axes = fig.add_subplot(2,1,2)
            axes.plot( Dist , mass , 'ro-' )
            axes.set_ylabel('Weight (kg)',axis_font)
            axes.set_xlabel('Range (NM)',axis_font)
            axes.grid(True)
            #plt.savefig(case_name + "_mission_R.pdf")
            plt.savefig(case_name + "_mission_R.png")            
        else:
            axes = fig.add_subplot(2,1,1)
            axes.plot( time , altitude , line_style )
            axes.set_ylabel('Altitude (ft)',axis_font)
            axes.grid(True)

#            axes = fig.add_subplot(3,1,3)
#            axes.plot( time , sfc , line_style )
#            axes.set_xlabel('Time (min)',axis_font)
#            axes.set_ylabel('sfc (lb/lbf-hr)',axis_font)
#            axes.grid(True)

            axes = fig.add_subplot(2,1,2)
            axes.plot( time , mass , 'ro-' )
            axes.set_ylabel('Weight (kg)',axis_font)
            axes.set_xlabel('Time (min)',axis_font)
            axes.grid(True)

            #plt.savefig(case_name + "_mission_t.pdf")
            plt.savefig(case_name + "_mission_t.png")
        
    # ------------------------------------------------------------------
    #   Velocities
    # ------------------------------------------------------------------
    fig = plt.figure("Velocities",figsize=(8,10))
    for segment in results.segments.values():

        time     = segment.conditions.frames.inertial.time[:,0] / Units.min
        Lift     = -segment.conditions.frames.wind.lift_force_vector[:,2]
        Drag     = -segment.conditions.frames.wind.drag_force_vector[:,0] / Units.lbf
        Thrust   = segment.conditions.frames.body.thrust_force_vector[:,0] / Units.lb
        velocity = segment.conditions.freestream.velocity[:,0]
        pressure = segment.conditions.freestream.pressure[:,0]
        density  = segment.conditions.freestream.density[:,0]
        EAS      = velocity * np.sqrt(density/1.225)
        mach     = segment.conditions.freestream.mach_number[:,0]
        Dist = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
        if x_axes == 'range':
            axes = fig.add_subplot(3,1,1)
            axes.plot( Dist , velocity / Units.kts, line_style )
            axes.set_ylabel('velocity (kts)',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,2)
            axes.plot( Dist , EAS / Units.kts, line_style )
            axes.set_xlabel('Range (NM)',axis_font)
            axes.set_ylabel('Equivalent Airspeed',axis_font)
            axes.grid(True)    
        
            axes = fig.add_subplot(3,1,3)
            axes.plot( Dist , mach , line_style )
            axes.set_xlabel('Range (NM)',axis_font)
            axes.set_ylabel('Mach',axis_font)
            axes.grid(True)
            #plt.savefig(case_name + "_velocity_R.pdf")
            plt.savefig(case_name + "_velocity_R.png")            
            
            
        else:
            axes = fig.add_subplot(3,1,1)
            axes.plot( time , velocity / Units.kts, line_style )
            axes.set_ylabel('velocity (kts)',axis_font)
            axes.grid(True)

            axes = fig.add_subplot(3,1,2)
            axes.plot( time , EAS / Units.kts, line_style )
            axes.set_xlabel('Time (min)',axis_font)
            axes.set_ylabel('Equivalent Airspeed',axis_font)
            axes.grid(True)    
        
            axes = fig.add_subplot(3,1,3)
            axes.plot( time , mach , line_style )
            axes.set_xlabel('Time (min)',axis_font)
            axes.set_ylabel('Mach',axis_font)
            axes.grid(True)
            #plt.savefig(case_name + "_velocity_t.pdf")
            plt.savefig(case_name + "_velocity_t.png")

            
    delimiter = ','       
    fid = open(case_name +'_mission_output.dat','w')   # Open output file
    fid.write('Output file with mission profile breakdown\n\n') #Start output printing
    fid.write('  Time  |   h    |  Mach  |  Range |  Mass  |   CL   |   CD   |   L/D  | Thrust |  Drag  |  CDi   |  CDP   |  sfc   |  sfc    |\n')
    fid.write('   min  |   m    |    -   |   NM   |   kg   |   -    |   -    |   -    |   kN   |   kN   |   -    |   -    |  1/h   |e-5kg/N/s|\n')
    for segment in results.segments.values():
        time     = segment.conditions.frames.inertial.time[:,0] / Units.min
        Lift     = -segment.conditions.frames.wind.lift_force_vector[:,2]
        Drag     = -segment.conditions.frames.wind.drag_force_vector[:,0]/1000 # in kN 
        CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
        CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
        aoa = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        l_d = CLift/CDrag
        velocity = segment.conditions.freestream.velocity[:,0]
        pressure = segment.conditions.freestream.pressure[:,0]
        density  = segment.conditions.freestream.density[:,0]
        EAS      = velocity * np.sqrt(density/1.225)
        
        mach     = segment.conditions.freestream.mach_number[:,0]
        aoa      = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        mass     = segment.conditions.weights.total_mass[:,0]
        altitude = segment.conditions.freestream.altitude[:,0] # in m / Units.ft
        mdot     = segment.conditions.weights.vehicle_mass_rate[:,0]
        thrust   = segment.conditions.frames.body.thrust_force_vector[:,0]/1000 # in kN
        sfc      = (mdot / Units.lb) / (thrust /Units.lbf) * Units.hr/1000 # in 1/h
        sfc_SI   = mdot/thrust/1000*100000 # in 10e-5kg/N/s
        drag_breakdown = segment.conditions.aerodynamics.drag_breakdown
        cdp = drag_breakdown.parasite.total[:,0]
        cdi = drag_breakdown.induced.total[:,0]
        cdc = drag_breakdown.compressible.total[:,0]
        cdm = drag_breakdown.miscellaneous.total[:,0]
        cd  = drag_breakdown.total[:,0]
#        print('segment test 0: ' + str(segment.conditions.frames.inertial.position_vector[0,0]))
#        print('segment test -1: ' + str(segment.conditions.frames.inertial.position_vector[-1,0]))
#        print('altitude test -1: ' + str(segment.conditions.freestream.altitude[-1,0]))
#        print('altitude test vec: ' + str(array(altitude)))
        
        
        Dist = segment.conditions.frames.inertial.position_vector[:,0]  / Units.nautical_miles
#        Dist = segment.conditions.frames.inertial.position_vector[-1,0]  / Units.nautical_miles
#        time_str =   str('%8.3f'   % time[0])     + '|'
#        h_str =   str('%8.2f'   % altitude[0])     + '|'
#        Ma_str =   str('%8.4f'   % mach[0])     + '|'
#        Dist_str =   str('%8.2f'   % Dist[0])     + '|'
#        mass_str =   str('%8.1f'   % mass[0])     + '|'
#        CL_str =   str('%8.5f'   % CLift[0])     + '|'
#        CD_str =   str('%8.5f'   % CDrag[0])     + '|'
#        L2D_str =   str('%8.3f'   % l_d[0])     + '|'
#        thrust_str =   str('%8.3f'   % thrust[0])     + '|'
#        cdi_str =   str('%8.5f'   % cdi[0])     + '|'
#        cdp_str =   str('%8.5f'   % cdp[0])     + '|'
#        sfc_str =   str('%8.5f'   % sfc[0])     + '|'
#        sfc_SI_str =   str('%9.5f'   % sfc_SI[0])     + '|'
        for i in range(len(time)):           
            time_str =   str('%8.3f'   % time[i])     + '|'
            h_str =   str('%8.2f'   % altitude[i])     + '|'
            Ma_str =   str('%8.4f'   % mach[i])     + '|'
            Dist_str =   str('%8.2f'   % Dist[i])     + '|'
            mass_str =   str('%8.1f'   % mass[i])     + '|'
            CL_str =   str('%8.5f'   % CLift[i])     + '|'
            CD_str =   str('%8.5f'   % CDrag[i])     + '|'
            L2D_str =   str('%8.3f'   % l_d[i])     + '|'
            thrust_str =   str('%8.3f'   % thrust[i])     + '|'
            Drag_str =   str('%8.3f'   % Drag[i])     + '|'
            cdi_str =   str('%8.5f'   % cdi[i])     + '|'
            cdp_str =   str('%8.5f'   % cdp[i])     + '|'
            sfc_str =   str('%8.5f'   % sfc[i])     + '|'
            sfc_SI_str =   str('%9.5f'   % sfc_SI[i])     + '|'        
            fid.write(time_str + h_str + Ma_str + Dist_str + mass_str + CL_str + CD_str + L2D_str + thrust_str + Drag_str + cdi_str + cdp_str + sfc_str + sfc_SI_str +'\n')
    fid.close

        
    return
# ----------------------------------------------------------------------
#   Module Test
# ----------------------------------------------------------------------
if __name__ == '__main__':
    print(' Error: No test defined ! ')   
