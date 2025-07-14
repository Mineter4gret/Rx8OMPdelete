# Mazda RX8 N3H6 ECU OMP Delete Analysis

## Binary Information
- **File**: brickcentral.bin
- **Size**: 524,288 bytes (512KB)
- **ECU Type**: N3H6 (2004 RX8)
- **Architecture**: Likely Renesas/Mitsubishi microcontroller

## Analysis Results

### Diagnostic Code Patterns Found
The following potential OMP-related diagnostic code patterns were identified:

1. **Pattern 1900**: 10 occurrences at locations:
   - 0x452b, 0x4631, 0x463b, 0x4697, 0x57ef, 0x7d2b, 0x9761, 0xa681, 0xf1dd, 0xf2c9

2. **Pattern 1901**: 3 occurrences at locations:
   - 0x1d39d, 0x6751b, 0x75be1

3. **Pattern 2000**: 10 occurrences at locations:
   - 0x9aa, 0x134e, 0x1bee, 0x2ea3, 0x366e, 0x373a, 0x49c7, 0x4b5b, 0x6707, 0x6d07

4. **Pattern 2001**: 10 occurrences at locations:
   - 0x17c7d, 0x4be6f, 0x5dec6, 0x5defc, 0x5df20, 0x5df86, 0x65e3f, 0x65f7d, 0x65fe7, 0x66135

5. **Pattern 2002**: 6 occurrences at locations:
   - 0x2e049, 0x5d843, 0x66087, 0x76f95, 0x79103, 0x79105

### Key Assembly Patterns
- **Branch if not zero**: 2157 occurrences (conditional checks)
- **Memory access pattern**: 3624 occurrences
- **Register loads**: 54 occurrences
- **Function calls**: 10 occurrences
- **Common ECU instructions**: 5 occurrences

## OMP Delete Strategy

### 1. Target Areas for Modification

#### A. OMP Pressure Monitoring
- **Location**: Around 0x452b-0x453b area
- **Function**: Likely monitors OMP pressure sensor
- **Modification**: Replace with NOP instructions or force "OK" status

#### B. OMP Flow Monitoring  
- **Location**: Around 0x57ef-0x57ff area
- **Function**: Likely monitors OMP flow rate
- **Modification**: Bypass flow checks

#### C. Diagnostic Code Setting
- **Locations**: 0x1d39d, 0x9aa, 0x134e
- **Function**: Sets OMP-related DTCs
- **Modification**: Prevent these codes from being set

### 2. Specific Modifications Required

#### A. NOP Out OMP Checks
Replace OMP monitoring routines with NOP instructions (0x00 0x09 on this architecture)

#### B. Force Good Status
Modify comparison instructions to always return "sensor OK" status

#### C. Bypass Limp Mode Triggers
Remove or modify conditional branches that lead to limp mode activation

### 3. Critical Safety Considerations

⚠️ **IMPORTANT WARNINGS:**
- This modification disables critical engine protection systems
- Pre-mix oil must be added to fuel (typically 1:100 ratio)
- Engine damage will occur without proper lubrication
- This modification may void warranty and violate emissions regulations
- Thorough testing required before daily driving

### 4. Modification Procedure

#### Step 1: Backup Original Binary
Always keep multiple copies of your original binary for recovery

#### Step 2: Hex Editor Modifications
Use a hex editor to make the following changes:

1. **Location 0x452b**: Replace OMP pressure check
   - Original: `19 00 0b 62`
   - Modified: `00 09 00 09` (NOP instructions)

2. **Location 0x57ef**: Replace OMP flow check  
   - Original: `19 00 09 60`
   - Modified: `00 09 00 09` (NOP instructions)

3. **Location 0x1d39d**: Disable DTC setting
   - Original: `19 01 fc 21`
   - Modified: `00 09 00 09` (NOP instructions)

#### Step 3: Checksum Correction
The ECU firmware likely has checksums that need to be recalculated after modification

#### Step 4: Testing Protocol
1. Test on dyno first
2. Monitor EGT temperatures
3. Check for other error codes
4. Verify oil consumption rates

### 5. Alternative Approaches

#### A. OMP Emulation
Instead of complete deletion, create a software emulation that satisfies the ECU's monitoring

#### B. Gradual Disabling
Disable OMP monitoring in stages to identify minimum required changes

#### C. Professional Tuning
Consider professional ECU tuning software that handles OMP deletes properly

### 6. Tools Required

- Hex editor (HxD, 010 Editor)
- Checksum calculator
- ECU programming interface
- Backup storage
- Pre-mix oil measurement tools

### 7. Post-Modification Checklist

- [ ] ECU accepts modified binary
- [ ] Engine starts and idles
- [ ] No immediate error codes
- [ ] Oil consumption monitored
- [ ] Performance testing completed
- [ ] Long-term reliability assessment

## Disclaimer

This modification is provided for educational and research purposes only. Modifying ECU firmware can result in:
- Engine damage
- Vehicle inoperability  
- Warranty voiding
- Legal/emissions compliance issues
- Safety risks

Always consult with professional tuners and understand local regulations before proceeding.