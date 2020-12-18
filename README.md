
# Concept

We want to log out information via the TransformTrace class to inform an interactive breakdown/view of what data has been captures, from where and what post prossesing has taken place.

What I'm trying to do is capture a simple overview with optional complexity (and have it created automatically).


# Types (for want of a better term)

Pipeline - the name of the pipeline, our starting node
Landing Page - a landing page for a pipeline
Distribution - a file taken from a landing page
Table - the data within a table

# Comments

The "comments" are captured via the TransformTracer against any one of the above types, I'm aiming at some variation
of "hidden unless requested", so you have a relatively simple flowdiagram but you can drill down into exactly what
each element is and how it was formed.

# This Repo

- I've mocked up the input data as "trace.json" (this isn't the structure the TransformTrace is logging things in at the moment but it's all data it has access to and could). 
- Flowchart.ttl is build from trace.json (you could arguably just output ttl from trasformTrace but this was easier)
- template.html makes it pretty

It's largely just Leigh's flowcharts with some automation and extra javascript.

# Running Locally

Navigate to this repo
- in the terminal run a local file server `python3 -m http.server --bind 127.0.0.1 3333`
- then browse to `http://127.0.0.1:3333/template.html`
