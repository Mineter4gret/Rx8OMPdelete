#!/usr/bin/env python3
"""
Firmware Analyzer - Diagnostic Tool
Compares different firmware versions to understand modification impacts.
"""

import os
import struct
from typing import Dict, List, Tuple

class FirmwareAnalyzer:
    def __init__(self):
        self.files = {
            'original': 'brickcentral.bin',
            'dangerous': 'brickcentral_omp_deleted.bin',
            'safe': 'brickcentral_omp_deleted_safe.bin', 
            'complete': 'brickcentral_omp_deleted_complete.bin'
        }
        self.data = {}
        
    def load_all_files(self) -> bool:
        """Load all available firmware files"""
        print("📂 Loading firmware files for analysis...")
        
        for name, filename in self.files.items():
            if os.path.exists(filename):
                try:
                    with open(filename, 'rb') as f:
                        self.data[name] = f.read()
                    print(f"  ✅ {name}: {len(self.data[name])} bytes")
                except Exception as e:
                    print(f"  ❌ {name}: Error - {e}")
            else:
                print(f"  ⚠️  {name}: Not found")
        
        return len(self.data) > 1
    
    def compare_modifications(self):
        """Compare modifications between versions"""
        print("\n🔍 Analyzing modifications...")
        
        if 'original' not in self.data:
            print("❌ Original firmware not available for comparison")
            return
        
        original = self.data['original']
        
        # Known modification locations
        locations = [
            {'addr': 0x452b, 'size': 4, 'desc': 'OMP pressure monitoring'},
            {'addr': 0x57ef, 'size': 4, 'desc': 'OMP flow monitoring'},
            {'addr': 0x1d39d, 'size': 4, 'desc': 'OMP DTC setting'},
            {'addr': 0x9aa, 'size': 2, 'desc': 'Limp mode trigger 1'},
            {'addr': 0x134e, 'size': 2, 'desc': 'Limp mode trigger 2'},
        ]
        
        print(f"\n{'Location':<8} {'Description':<25} {'Original':<12} {'Dangerous':<12} {'Safe':<12} {'Complete':<12}")
        print("-" * 85)
        
        for loc in locations:
            addr = loc['addr']
            size = loc['size']
            desc = loc['desc']
            
            if addr + size > len(original):
                continue
                
            orig_bytes = original[addr:addr+size]
            orig_hex = ' '.join(f'{b:02x}' for b in orig_bytes)
            
            line = f"0x{addr:04x}   {desc:<25} {orig_hex:<12}"
            
            for version in ['dangerous', 'safe', 'complete']:
                if version in self.data:
                    mod_bytes = self.data[version][addr:addr+size]
                    mod_hex = ' '.join(f'{b:02x}' for b in mod_bytes)
                    if mod_bytes != orig_bytes:
                        line += f" {mod_hex:<12}"
                    else:
                        line += f" {'unchanged':<12}"
                else:
                    line += f" {'N/A':<12}"
            
            print(line)
    
    def analyze_checksums(self):
        """Analyze checksum areas in all versions"""
        print("\n🔧 Analyzing checksums...")
        
        checksum_areas = [
            {'addr': 0x7EFFC, 'name': 'Main Program'},
            {'addr': 0x1FFFC, 'name': 'Calibration'}, 
            {'addr': 0x7FFFC, 'name': 'Boot Block'},
        ]
        
        print(f"\n{'Area':<15} {'Original':<12} {'Dangerous':<12} {'Safe':<12} {'Complete':<12}")
        print("-" * 65)
        
        for area in checksum_areas:
            addr = area['addr']
            name = area['name']
            
            line = f"{name:<15}"
            
            for version in ['original', 'dangerous', 'safe', 'complete']:
                if version in self.data and addr + 4 <= len(self.data[version]):
                    checksum = struct.unpack('>L', self.data[version][addr:addr+4])[0]
                    line += f" 0x{checksum:08x} "
                else:
                    line += f" {'N/A':<10}"
            
            print(line)
    
    def find_differences(self):
        """Find all differences between versions"""
        print("\n🔍 Finding all differences from original...")
        
        if 'original' not in self.data:
            return
        
        original = self.data['original']
        
        for version_name, version_data in self.data.items():
            if version_name == 'original' or len(version_data) != len(original):
                continue
                
            print(f"\n--- {version_name.upper()} vs ORIGINAL ---")
            
            differences = []
            for i in range(min(len(original), len(version_data))):
                if original[i] != version_data[i]:
                    differences.append(i)
            
            if differences:
                print(f"Total differences: {len(differences)} bytes")
                
                # Group consecutive differences
                groups = []
                current_group = [differences[0]]
                
                for i in range(1, len(differences)):
                    if differences[i] == differences[i-1] + 1:
                        current_group.append(differences[i])
                    else:
                        groups.append(current_group)
                        current_group = [differences[i]]
                groups.append(current_group)
                
                print("Difference regions:")
                for group in groups[:10]:  # Show first 10 groups
                    start = group[0]
                    end = group[-1]
                    if start == end:
                        orig_byte = original[start]
                        mod_byte = version_data[start]
                        print(f"  0x{start:06x}: 0x{orig_byte:02x} → 0x{mod_byte:02x}")
                    else:
                        print(f"  0x{start:06x}-0x{end:06x}: {len(group)} bytes changed")
                
                if len(groups) > 10:
                    print(f"  ... and {len(groups) - 10} more regions")
            else:
                print("No differences found")
    
    def check_file_integrity(self):
        """Check basic file integrity"""
        print("\n🔍 File integrity check...")
        
        for name, data in self.data.items():
            print(f"\n{name.upper()}:")
            print(f"  Size: {len(data)} bytes")
            
            # Check for obvious corruption
            zero_count = data.count(0x00)
            ff_count = data.count(0xFF)
            
            print(f"  Zero bytes: {zero_count} ({zero_count/len(data)*100:.1f}%)")
            print(f"  FF bytes: {ff_count} ({ff_count/len(data)*100:.1f}%)")
            
            if zero_count > len(data) * 0.5:
                print("  ⚠️  WARNING: High zero count - possible corruption")
            if ff_count > len(data) * 0.5:
                print("  ⚠️  WARNING: High FF count - possible erased areas")
            
            # Check entropy (basic measure)
            unique_bytes = len(set(data))
            print(f"  Unique bytes: {unique_bytes}/256 ({unique_bytes/256*100:.1f}%)")
            
            if unique_bytes < 50:
                print("  ⚠️  WARNING: Low entropy - possible corruption")
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n📊 DIAGNOSTIC SUMMARY")
        print("=" * 50)
        
        if len(self.data) < 2:
            print("❌ Insufficient files for meaningful analysis")
            return
        
        print("\n🎯 KEY FINDINGS:")
        
        # Check if modifications are present
        if 'original' in self.data:
            has_mods = {}
            original = self.data['original']
            
            test_locations = [0x452b, 0x57ef, 0x1d39d, 0x9aa, 0x134e]
            
            for version in ['dangerous', 'safe', 'complete']:
                if version in self.data:
                    mods = 0
                    for addr in test_locations:
                        if addr + 2 <= len(self.data[version]):
                            if self.data[version][addr:addr+2] != original[addr:addr+2]:
                                mods += 1
                    has_mods[version] = mods
            
            print("\nModifications applied:")
            for version, count in has_mods.items():
                print(f"  {version}: {count}/5 locations modified")
        
        print("\n🔧 RECOMMENDATIONS:")
        print("1. All our tools may have fundamental checksum issues")
        print("2. Need to find confirmed working OMP delete examples")
        print("3. Consider professional ECU tuning software")
        print("4. Test with minimal modifications first")
        print("5. Verify NOP instruction opcodes for Renesas architecture")
        
        print("\n⚠️  CRITICAL: Our approach needs revision based on proven examples")
    
    def run_analysis(self) -> bool:
        """Run complete firmware analysis"""
        print("🔬 FIRMWARE DIAGNOSTIC ANALYZER")
        print("=" * 40)
        
        if not self.load_all_files():
            print("❌ Failed to load firmware files")
            return False
        
        self.check_file_integrity()
        self.compare_modifications()
        self.analyze_checksums()
        self.find_differences()
        self.generate_report()
        
        return True

def main():
    """Main function"""
    analyzer = FirmwareAnalyzer()
    return analyzer.run_analysis()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)