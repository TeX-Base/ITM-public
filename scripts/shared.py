import argparse

def parse_default_arguments() -> argparse.Namespace:
    return get_default_parser().parse_args()
    
def get_default_parser() -> argparse.ArgumentParser:
    # TODO: All the --foo and --no-foo module arguments should have the same default.
    parser = argparse.ArgumentParser()
    parser.add_argument('--human', default=False, help="Allows human to give selections at command line", action='store_true')
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, default=True, help="Turns logging on/off (default on)")
    parser.add_argument('--ebd', action=argparse.BooleanOptionalAction, default=False, help="Turns Event Based Diagnosis analyzer on/off (default off)")
    parser.add_argument('--mc', action=argparse.BooleanOptionalAction, default=True, help="Turns Monte Carlo Analyzer on/off (default on)")
    parser.add_argument('--br', action=argparse.BooleanOptionalAction, default=True, help="Turns Bounded Rationalizer on/off (default on)")
    parser.add_argument('--keds', action=argparse.BooleanOptionalAction, default=True, help="Uses KDMA Estimation Decision Selector for decision selection (default)")
    parser.add_argument('--kedsd', action=argparse.BooleanOptionalAction, default=False, help="Uses KDMA with Drexel cases")
    parser.add_argument('--csv', action=argparse.BooleanOptionalAction, default=False, help="Uses CSV Decision Selector")
    parser.add_argument('--bayes', action=argparse.BooleanOptionalAction, default=True, help='Perform bayes net calculations')
    parser.add_argument('--dump', action=argparse.BooleanOptionalAction, default=True, help="Dumps probes out for UI exploration.")
    parser.add_argument('--rollouts', type=int, default=1600, help="Monte Carlo rollouts to perform")
    parser.add_argument('--endpoint', type=str, help="The URL of the TA3 api", default=None)
    parser.add_argument('--variant', type=str, help="TAD variant", default="aligned")
    parser.add_argument('--training', action=argparse.BooleanOptionalAction, default=True, help="Asks for KDMA associations to actions")
    parser.add_argument('--session_type', type=str, default='eval', help="Modifies the server session type. possible values are 'soartech', 'adept', and 'eval'. Default is 'eval'.")
    parser.add_argument('--scenario', type=str, default=None, help="ID of a scenario that TA3 can play back.")
    parser.add_argument('--kdma', dest='kdmas', type=str, action='append', help="Adds a KDMA value to alignment target for selection purposes. Format is <kdma_name>-<kdma_value>")
    parser.add_argument('--evaltarget', dest='eval_targets', type=str, action='append', help="Adds an alignment target name to request evaluation on. Must match TA1 capabilities, requires --training.")
    parser.add_argument('--selector', default=None, help=argparse.SUPPRESS)
    return parser

