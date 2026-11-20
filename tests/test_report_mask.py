
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mailrecon.report import mask

print("===== MAILRECON EMAIL MASKING TEST =====")

print("\nTest 1:")
print(mask("john.smith@example.com"))

print("\nTest 2:")
print(mask("mary.jones@gmail.com"))

print("\nTest 3:")
print(mask("adam.lee@yahoo.com"))

print("\nTest 4: Invalid email")
print(mask("invalid-email"))

print("\n===== TEST COMPLETED =====")
