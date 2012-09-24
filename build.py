"""
Simple static page generator.
Uses jinja2 to compile templates.
Templates should live inside `./templates` and will be compiled in '.'.
"""
import csv
import os
import sys

from hamlish_jinja import HamlishExtension
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = "./templates"


def build_template(env, template_name, **kwargs):
    """Compile a template.
    *   env should be a Jinja environment variable indicating where to find the
        templates.
    *   template_name should be the name of the template as it appears inside
        of `./templates`.
    *   kwargs should be a series of key-value pairs. These items will be
        passed to the template to be used as needed.
    """
    name, ext = os.path.splitext(template_name)
    print "Building %s..." % template_name
    template = env.get_template(template_name)
    output_name = '%s.html' % name
    with open(output_name, "w") as f:
        f.write(template.render(**kwargs))


def parse_csv(filename):
    """Read data from a CSV.
    This will return a list of dictionaries, with key-value pairs corresponding
    to each column in the parsed csv.
    """
    with open(filename, 'rb') as f:
        return list(csv.DictReader(f))


def main():
    """Compile each of the templates."""
    env = Environment(loader=FileSystemLoader(searchpath=TEMPLATE_DIR),
                      extensions=[HamlishExtension])

    # Add any instructions to build templates here
    filenames = os.listdir(TEMPLATE_DIR)
    for filename in filenames:
        # Don't compile partials or hidden files
        if not (filename.startswith('_') or filename.startswith(".")):
            build_template(env, filename)
    print "Templates built."
    return 0


if __name__ == "__main__":
    main()

    if len(sys.argv) > 1 and sys.argv[1] == '--watch':
        import time

        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class JinjaEventHandler(FileSystemEventHandler):
            """
            Naive recompiler.
            Rebuilds all templates if anything changes in /templates.
            """
            def on_modified(self, event):
                print "Recompiling templates..."
                super(JinjaEventHandler, self).on_created(event)
                if event.src_path.endswith("/templates"):
                    main()

        # Start watching for any changes
        event_handler = JinjaEventHandler()
        observer = Observer()
        observer.schedule(event_handler, path=TEMPLATE_DIR)
        observer.start()
        print "Watching '%s' for changes..." % TEMPLATE_DIR
        print "Press Ctrl+C to stop."
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        print "Process killed"
        observer.join()
