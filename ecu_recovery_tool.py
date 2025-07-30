#!/usr/bin/env python3
"""
ECU Recovery Tool - Mazda RX8 N3H6
Simple tool to help recover from soft brick by preparing original firmware for reflashing.
"""

import os
import shutil
import hashlib
from datetime import datetime

class ECURecoveryTool:
    def __init__(self):
        self.backup_file = "brickcentral.bin.backup_20250714_011624"
        self.recovery_file = "RECOVERY_brickcentral.bin"
        
    def verify_backup_exists(self):
        """Verify the original backup file exists"""
        if os.path.exists(self.backup_file):
            size = os.path.getsize(self.backup_file)
            print(f"✅ Original backup found: {self.backup_file}")
            print(f"   File size: {size} bytes ({size/1024:.1f} KB)")
            return True
        else:
            print(f"❌ ERROR: Backup file not found: {self.backup_file}")
            print("   Cannot proceed with recovery without original backup!")
            return False
    
    def calculate_file_hash(self, filename):
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filename, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return None
    
    def prepare_recovery_file(self):
        """Prepare the recovery file from backup"""
        print(f"\n📁 Preparing recovery file...")
        
        try:
            # Copy backup to recovery file
            shutil.copy2(self.backup_file, self.recovery_file)
            
            # Verify copy
            backup_hash = self.calculate_file_hash(self.backup_file)
            recovery_hash = self.calculate_file_hash(self.recovery_file)
            
            if backup_hash == recovery_hash:
                print(f"✅ Recovery file prepared: {self.recovery_file}")
                print(f"   MD5 Hash: {recovery_hash}")
                return True
            else:
                print("❌ ERROR: File copy verification failed!")
                return False
                
        except Exception as e:
            print(f"❌ ERROR preparing recovery file: {e}")
            return False
    
    def display_recovery_instructions(self):
        """Display step-by-step recovery instructions"""
        print("\n" + "="*60)
        print("🔧 ECU RECOVERY INSTRUCTIONS")
        print("="*60)
        
        print(f"""
📋 WHAT TO DO NOW:

1. 🔌 PREPARE HARDWARE:
   - Get ECU programming tool (K-Tag, MPPS, BDM100, etc.)
   - Use external 12V power supply (NOT vehicle battery)
   - Ensure stable power throughout programming

2. 💾 USE THIS FILE FOR RECOVERY:
   File: {self.recovery_file}
   This is your ORIGINAL, UNMODIFIED firmware

3. 🔧 RECOVERY PROCESS:
   a) Connect programming tool to ECU
   b) Try OBD communication first
   c) If OBD fails, use BDM mode
   d) Flash the {self.recovery_file}
   e) Verify ECU communication after flash

4. ⚠️  CRITICAL SAFETY:
   - Do NOT start engine until recovery is complete
   - Do NOT disconnect power during programming
   - Have backup power ready in case of interruption

5. ✅ VERIFY RECOVERY:
   - ECU should communicate via OBD
   - Engine should start and idle normally
   - No new error codes should appear

🆘 IF YOU'RE UNSURE:
   - Contact professional ECU tuner
   - Bring them the {self.recovery_file}
   - Explain the soft brick situation

📞 EMERGENCY: If recovery fails, this indicates a deeper
   hardware issue requiring professional intervention.
""")
    
    def check_modified_firmware(self):
        """Check if the modified firmware exists and analyze it"""
        modified_file = "brickcentral_omp_deleted.bin"
        
        if os.path.exists(modified_file):
            print(f"\n🔍 Modified firmware found: {modified_file}")
            
            # Compare sizes
            backup_size = os.path.getsize(self.backup_file)
            modified_size = os.path.getsize(modified_file)
            
            if backup_size == modified_size:
                print(f"   Same size as original: {modified_size} bytes")
                
                # Calculate hashes
                backup_hash = self.calculate_file_hash(self.backup_file)
                modified_hash = self.calculate_file_hash(modified_file)
                
                if backup_hash != modified_hash:
                    print(f"   ⚠️  Modified firmware detected (different hash)")
                    print(f"   Original:  {backup_hash}")
                    print(f"   Modified:  {modified_hash}")
                    print(f"   🔧 Issue: Modified firmware lacks proper checksums")
                else:
                    print(f"   ✅ Files are identical (unexpected)")
            else:
                print(f"   ⚠️  Size mismatch: Modified={modified_size}, Original={backup_size}")
    
    def run_recovery_prep(self):
        """Run the complete recovery preparation process"""
        print("🚨 ECU SOFT BRICK RECOVERY TOOL")
        print("===============================")
        print("This tool will help you recover from the OMP delete soft brick.\n")
        
        # Check if backup exists
        if not self.verify_backup_exists():
            return False
        
        # Analyze the situation
        self.check_modified_firmware()
        
        # Prepare recovery file
        if not self.prepare_recovery_file():
            return False
        
        # Display instructions
        self.display_recovery_instructions()
        
        print("\n" + "="*60)
        print("✅ RECOVERY PREPARATION COMPLETE")
        print("="*60)
        print(f"Recovery file ready: {self.recovery_file}")
        print("Follow the instructions above to restore your ECU.")
        
        return True

def main():
    """Main function"""
    tool = ECURecoveryTool()
    success = tool.run_recovery_prep()
    
    if success:
        print("\n🎯 Next steps: Use ECU programming tool to flash the recovery file.")
    else:
        print("\n❌ Recovery preparation failed. Check errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)