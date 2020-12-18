
import json

def get_base(name, id_landing_pages, id):
    return """
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix cogsgit: <https://github.com/GSS-Cogs/> .
@prefix cogs: <http://gss-cogs.uk/def/arch/> .

<http://gss-cogs.uk/def/arch> a owl:Ontology;
rdfs:label "Transform Mapping" ;
.

cogs:SoftwarePackage a owl:Class ;
rdfs:label "Software package" ;
.
cogs:SoftwarePackage a owl:Class ;
rdfs:label2 "Label2" ;
.
cogs:Pipeline a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Pipeline" ;
.
cogs:Distribution a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Distribution" ;
.
cogs:LandingPage a owl:Class ;
  rdfs:subClassOf cogs:SoftwarePackage ;
  rdfs:label "Landing Page" ;
.
cogs:Datasets a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Output Dataset" ;
.
cogs:Table a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Table Name";
.
cogs:Columns a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Table" ;
.
cogs:PMD a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "PMD" ;
.
cogs:Rename a owl:Class ;
rdfs:subClassOf cogs:SoftwarePackage ;
rdfs:label "Output" ;
.

# Initial Pipeline element
cogsgit:top-level a cogs:Source ;
rdfs:label "Pipeline";
rdfs:label2 "{name}";
rdfs:resource "{id}";
{landing_page_links}

""".format(name=name, landing_page_links="\n".join(["cogs:scrape cogsgit:{} ; ".format(x) for x in id_landing_pages])+" . ", id=id)

def build_description(columns):
    """
    I'm using rdfs:description to hold the column comments being logged out by the TransformTracer.
    All we're doing here is putting them into a sensibly formatted string ready for display on the front end
    """
    lines = [""]
    for column in columns:
        for name, comments in column.items():
            lines.append("\n<strong>" + name + "</strong>\n")
            if len(comments) > 0:
                lines += comments
            else:
                lines.append("<i>no comments at this stage</i>")
            lines.append("")
            

    # Now style it to a 40 character maximum
    # ewwww
    description = ""
    for line in lines:
        if line == "":
            description += "<br>"
        else:
            if len(line) > 35:
                line_so_far = ""
                tokens = line.split(" ")
                for i in range(0, len(tokens)):
                    if len(line_so_far + " "+ tokens[i]) > 34:
                        description += line_so_far + "<br>"
                        line_so_far = tokens[i]
                    else:
                        line_so_far += " "+ tokens[i]
                description += line_so_far + "<br>"
            else:
                description += line + "<br>"
    return '""'+ description.strip()+'""'

def make_ttl(trace_json_path="./trace.json"):
    """
    Given an input of a trace.json, generate ttl sufficiant to populate
    template.html
    """

    try:
        with open(trace_json_path, "r") as f:
            data = json.load(f)
    except Exception as err:
        raise Exception("Unable to load the provided trace json {}".format(trace_json_path)) from err
    
    rdf_as_text = get_base(data["name"], [x["id"] for x in data["landing_page"]], data["id"])

    for landing_page in data["landing_page"]:
        
        # Add a "Landing Page" box
        rdf_as_text += "# A landing page and the source(s) being drawn from it\n"
        rdf_as_text += 'cogsgit:{landing_page_id} a cogs:LandingPage ; rdfs:resource "{landing_page_id}" ; rdfs:label "Landing Page" ; rdfs:comment "{landing_page_url}" ; \n' \
                                    .format(landing_page_id=landing_page['id'], landing_page_url=landing_page['url'])

        # Link Sources to Landing Page
        rdf_as_text += "cogs:scrape " + "".join(["cogsgit:{};".format(x["id"]) for x in landing_page["source"]]) + " . \n\n"

        # Now iterate and add the tables within each source
        for source in landing_page["source"]:

            rdf_as_text += 'cogsgit:{source_id} a cogs:Source ; rdfs:label "Distribution" ; rdfs:resource "{source_id}" ; rdfs:comment "{source_name}" ;' \
                    .format(source_id=source["id"], source_name=source["name"])
            rdf_as_text += "".join(['cogs:transforms cogsgit:{} ; '.format(x["id"]) for x in source["tables"]]) + " . \n\n"
            
            # Add individual Tables from that source
            for table in source["tables"]:
                rdf_as_text += 'cogsgit:{table_id} a cogs:Table ; rdfs:resource "{table_id}" ; rdfs:label "Table" ; rdfs:comment "{name}" ; rdfs:description "{description}" ; '.strip() \
                                    .format(table_id=table['id'], name=table['name'], description=build_description(table["columns"]))

                if "child" not in table.keys():
                    rdf_as_text += 'cogs:joins cogsgit:pmd1 ; . \n'
                else:
                    rdf_as_text += 'cogs:joins cogsgit:{} ; . \n'.format(table["child"])
            
            # Break and space
            rdf_as_text += "\n"
        rdf_as_text += "\n"

    # Add any child tables

    if len(data["children"]) > 0:
        rdf_as_text += '# Children (aka Merged Tables) created from combinations of initial tables and other Merged Tables\n'

    for table in data["children"]:

        # Add a "Source" box
        rdf_as_text += 'cogsgit:{table_id} a cogs:Table ; rdfs:label "Table" ; rdfs:resource "{table_id}" ; rdfs:comment "{name}" ; rdfs:description "{description}" ; ' \
                                    .format(table_id=table['id'], name=table['name'], description=build_description(table["columns"]))

        if "child" not in table.keys():
            rdf_as_text += 'cogs:uploads cogsgit:pmd1 ; .\n'
        else:
            rdf_as_text += 'cogs:joins cogsgit:{};  . '.format(table["child"])

    # Break and space
    rdf_as_text += "\n"

    rdf_as_text += """
cogsgit:pmd1 a cogs:PMD ;
  rdfs:label "PMD" ;
  rdfs:resource "0";
  rdfs:comment <{}> ;
.
    """.format(r"https://staging.gss-data.org.uk/datasets?columns=http%3A%2F%2Fpurl.org%2Fdc%2Fterms%2Fpublisher")
    with open("flowchart.ttl", "w") as f:
        f.write(rdf_as_text)

make_ttl()