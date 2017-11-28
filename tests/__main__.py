
import os
import unittest
import argparse

def main(hypothesis=False):
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='hyp*.py' if hypothesis else 'test*.py')
    
    runner = unittest.TextTestRunner()
    print('Running unit tests:')
    runner.run(suite)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--hypothesis', action='store_true', help='Run random tests using hypothesis')
    args = parser.parse_args()
    main(args.hypothesis)
