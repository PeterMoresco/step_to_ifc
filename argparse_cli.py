import argparse
import os


def main():
    # Create the parser
    my_parser = argparse.ArgumentParser(
        description='Convert a STEP assembly to IFC.')
    # Add the arguments
    my_parser.add_argument('freecad_path',
                           metavar='freecad_path',
                           type=str,
                           help='Path to the FreeCAD folder')
    my_parser.add_argument('step_fpath',
                           metavar='step_fpath',
                           type=str,
                           help='Path to the STEP file')
    my_parser.add_argument('ifc_fpath',
                           metavar='ifc_fpath',
                           type=str,
                           help='Path to the output ifc file')
    # Parse the args
    args = my_parser.parse_args()

    # Check the input step file path
    if not os.path.exists(args.step_fpath):
        raise Exception('Theres no file {}'.format(args.step_fpath))
    # Check for the FreeCAD folder
    freecad_fpath = args.freecad_path
    freecad_python = os.path.join(freecad_fpath, 'bin', 'python.exe')
    if not os.path.exists(freecad_python):
        raise Exception('Theres any python.exe in {}'.format(freecad_fpath))


if __name__ == '__main__':
    main()
