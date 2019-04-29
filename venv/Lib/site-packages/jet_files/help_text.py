from jet_files import helper_functions as hf


def help_text():
    if not hf.already_initialized():
        print ("Please init a jet repo before calling other commands")
        return
    # No point re-writing documentation, so just link to it.
    print ("For help, please visit www.jetvc.co.uk/documentation/")


def run():
    help_text()
