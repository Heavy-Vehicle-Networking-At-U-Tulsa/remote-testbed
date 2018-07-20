# Proposed Contributions
   -*Numbers are the order of the changes/tests to/on the testbed.*

## Simplicity
1. Clean up Files
   -*Remove unnecessary code/files leftover from Joe/Ethan to eliminate confusion for groups following up research on this testbed.*
2. Make Testbed Setup Simpler
   -*Instead of executing 5 scripts, only run one executable.*

## Efficiency
3. Change vehicle message logging mechanism 
   -*Instead of logging on beaglebone, send data to database directly with StartLogging request.*
4. Parse Logs on User Interface rather than BeagleBone
   -*Create a new page to select the interface, parameter, and units for the plot.*

## Testing
5. Check if Frames are Dropped
6. Determine Latency
7. Log data in the format specified here: https://github.com/Heavy-Vehicle-Networking-At-U-Tulsa/NMFTA-CAN-Logger
8. Perform diagnostics tests while logging.

## Solve Timestamp Problem
9. Connect BeagleBone to Server to get Timestamp on Boot
   -*Power loss causes no data to be returned because of incorrect timestamps.*

## Additional Features
10. View/Parse Log Files on Front Interface
   -*Filter interface, priority, pgn, destination address, source address, and full ID.*
11. Loop Simulation Commands as a Whole
   -*Create a Loop Drive button to loop all simulation commands for a duration of time.*
12. Create Default Drive
   -*Implement button to create a default drive where preset simulation commands exist.*

## Ambitious Goals (if time permits)
13. Live Data
   -*Ability to filter incoming data and view live plots.*
14. Live Commands
   -*Send Commands/Messages while Viewing Live Data to see Effects.*