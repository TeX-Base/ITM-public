import argparse, sys

def validate_args(args: argparse.Namespace) -> None:

    # TODO: Eventually, we'll *only* have --selector. For now, we accept both and using one approach sets the other one appropriately
    decision_selectors = [ args.keds, args.kedsd, args.human ]

    if sum(decision_selectors) > 1:
        sys.stderr.write("\x1b[93mAt most one of ({arglist}) may be set (All are deprecated in favor of --selector).\x1b[0m\n")
        sys.exit(1)


    # Make the two approaches consistent with each other. TODO: remove once the --selector appraoch is mandatory
    if args.keds: args.selector = 'keds'
    elif args.kedsd: args.selector = 'kedsd'
    elif args.human: args.selector = 'human'
    
    if args.session_type != 'eval' and args.selector in ['keds', 'kedsd', 'csv'] and args.kdmas is None:
        sys.stderr.write("\x1b[93mYour selected decision selector requires an alignment target. "
                         + "Provide one by running in evaluation mode (--session_type eval), or "
                         + "by listing kdmas explicitly (e.g., --kdma mission=.8 --kdma denial=.5)."
                         + "\x1b[0m\n"
                        )
        sys.exit(1)
        
    if args.session_type == 'eval' and args.scenario is not None:
        sys.stderr.write("\x1b[93mCannot specify a scenario in evaluation mode.\x1b[0m\n")
        sys.exit(1)

    if args.session_type == 'eval' and args.kdmas is not None:
        sys.stderr.write("\x1b[93mPlease do not supply your own KDMAs in evaluation mode.\x1b[0m\n")
        sys.exit(1)

    if args.eval_targets is not None and len(args.eval_targets) > 0 and not args.training:
        args.training = True

    if args.session_type == 'eval' and args.training:
        sys.stderr.write("\x1b[93mCannot perform training in evaluation mode.\x1b[0m\n")
        sys.exit(1)
    
    #args.keds = ('keds' == args.selector)
    #args.kedsd = ('kedsd' == args.selector)
    #args.csv = ('csv' == args.selector)
    #args.human = ('human' == args.selector)
    

def parse_default_arguments() -> argparse.Namespace:
    args = get_default_parser().parse_args()
    validate_args(args)

    return args
    
def get_default_parser() -> argparse.ArgumentParser:
    # TODO: All the --foo and --no-foo module arguments should have the same default.
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, default=True, help="Turns logging on/off (default on)")
    parser.add_argument('--dump', action=argparse.BooleanOptionalAction, default=True, help="Dumps probes out for UI exploration.")
    parser.add_argument('--rollouts', type=int, default=256, help="Monte Carlo rollouts to perform")
    parser.add_argument('--endpoint', type=str, help="The URL of the TA3 api", default=None)
    parser.add_argument('--variant', type=str, help="TAD variant", default="aligned", choices=["aligned", "misaligned", "baseline", "severity-baseline"])
    parser.add_argument('--session_type', type=str, default='eval',
        help="Modifies the server session type. possible values are 'soartech', 'adept', and 'eval'. Default is 'eval'.",
        choices = ["soartech", "adept", "eval"])
    parser.add_argument('--scenario', type=str, default=None, help="ID of a scenario that TA3 can play back.")
    parser.add_argument('--kdma', dest='kdmas', type=str, action='append', help="Adds a KDMA value to alignment target for selection purposes. Format is <kdma_name>-<kdma_value>")
    parser.add_argument('--training', action=argparse.BooleanOptionalAction, default=False, help="Asks for KDMA associations to actions")
    parser.add_argument('--evaltarget', dest='eval_targets', type=str, action='append', help="Adds an alignment target name to request evaluation on. Must match TA1 capabilities, implies --training.")
    parser.add_argument('--selector', default='random', choices=['keds', 'kedsd', 'human', 'random'], help="Sets the decision selector") # TODO: add details of what each option does
    parser.add_argument('--selector-object', default=None, help=argparse.SUPPRESS)
    parser.add_argument('--seed', type=int, default=None, help="Changes the random seed to be used during this run; must be an integer")
    parser.add_argument('--casefile', type=str, default=None, 
                        help="Provides cases to be used in making decisions by the decision "\
                             + "selector. Used with keds, kedsd, not otherwise.")
    parser.add_argument('--weightfile', type=str, default=None, 
                        help="Provides weights to be used in comparing cases by the decision "\
                             + "selector. Used with keds, kedsd, not otherwise.")
    parser.add_argument('--uniformweight', action=argparse.BooleanOptionalAction, default=False, 
                        help="Requests that a default uniform weight be used in comparing cases "\
                             + "by the decision selector. Overrides --weightfile. Used with keds, "\
                             + "kedsd, not otherwise.")
    parser.add_argument('--decision_verbose', action=argparse.BooleanOptionalAction, default=False, 
                        help="Causes a decision selector to output extra information explaining its selections.")



    selectors = parser.add_argument_group('Decision Selectors', description='Exactly one of these must be enabled (or --selector must be set). \x1b[93m(Deprecated in favor of --selector)\x1b[0m')
    selectors.add_argument('--keds', action=argparse.BooleanOptionalAction, default=False, help="Uses KDMA Estimation Decision Selector for decision selection (default)")
    selectors.add_argument('--kedsd', action=argparse.BooleanOptionalAction, default=False, help="Uses KDMA with Drexel cases")
    selectors.add_argument('--human', default=False, help="Allows human to give selections at command line", action='store_true')
    
    analyzers = parser.add_argument_group('Decision Analyzers', description='Any or all of these can be enabled')
    analyzers.add_argument('--ebd', action=argparse.BooleanOptionalAction, default=False, help="Turns Event Based Diagnosis analyzer on/off (default off)") # TODO: default to on
    analyzers.add_argument('--mc', action=argparse.BooleanOptionalAction, default=True, help="Turns Monte Carlo Analyzer on/off (default on)")
    analyzers.add_argument('--br', action=argparse.BooleanOptionalAction, default=True, help="Turns Bounded Rationalizer on/off (default on)")
    analyzers.add_argument('--bayes', action=argparse.BooleanOptionalAction, default=True, help='Perform bayes net calculations')
    
    return parser

