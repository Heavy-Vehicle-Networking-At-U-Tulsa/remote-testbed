#Proposed Contributions
##Testbed Updates
1. Change vehicle message logging mechanism 
   *Instead of logging on beaglebone, send data to database directly with StartLogging request.*
2. Make Testbed Setup Simpler
   *Instead of executing 5 scripts, only run one executable.*
3. Parse Logs for Graphing on User Interface
   *Instead of resending parsed plottable data from BeagleBone, parse on UI.*
4. Loop SSS2 Commands
   *Instead of repeating simulation commands by inputting them, click a Loop Drive button to loop all simulation commands.*
5. Create Default Drive
   *Implement button to create a default drive where preset simulation commands exist that can be looped for a specified time.*
6. Clean up Files
   *Remove unnecessary code/files leftover from Joe/Ethan to eliminate confusion for groups following up research on this testbed.*
7. Fix Time Issues
   *No data is returned if the testbed loses power and BeagleBones are reset because of incorrect system timestamps. Fix this.*
##Testing
1. Check if Frames are Dropped
2. Determine Latency
##Ambitious Goals (if time permits)
1. Select SPN/PGN from Dropdown to Select a Plot on Plot Page to Graph from Log File on Database
   *Only implement a couple for proof of concept.*
2. Live Data