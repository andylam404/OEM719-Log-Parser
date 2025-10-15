import os
from parsers.oem719_parser import parse_oem719_log

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_file = os.path.join(base_dir, "LabVIEW_Python_Interview_Prompt_1",
                               "LabVIEW Python Interview Prompt", "OEM719 Simulated Log.txt")

    src_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(src_dir, "test_data")

    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")

    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    parse_oem719_log(input_file, output_dir)

if __name__ == "__main__":
    main()
