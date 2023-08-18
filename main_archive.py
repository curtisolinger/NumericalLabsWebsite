import os
import re
from flask import Flask, render_template, session, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from semigroups import (
    create_semigroup,
    calc_num_of_elements_of_len_k,
    create_invariants,
    create_factorization_fig,
    create_example_1,
    create_invariants_for_single_element,
)

# Set the max factorization length to which you wish to examine
N = 20
app = Flask(__name__)
bootstrap = Bootstrap5(app)
# $ python -c 'import secrets; print(secrets.token_hex())'
website_key = os.environ.get('SITE_KEY')
print(website_key)
app.config['SECRET_KEY'] = 'mysecretkey'
gen1 = [2, 3]
gen2 = [3, 5]
gen3 = [2, 3]


class GeneratorForm1(FlaskForm):
    generators1 = StringField('Generators (comma-separated)', validators=[
        DataRequired()])
    submit = SubmitField('Submit')


class GeneratorForm2(FlaskForm):
    generators2 = StringField('Generators (comma-separated)', validators=[
        DataRequired()])
    submit = SubmitField('Submit')


class GeneratorForm3(FlaskForm):
    generators3 = StringField('Generators (comma-separated)', validators=[
        DataRequired()])
    single_element = IntegerField('Element', validators=[
        DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/semigroups2')
def semigroups2():
    return render_template('semigroups2.html')


@app.route('/calculateSemigroup', methods=['POST'])
def calculate_semigroup():
    data = request.form['gen01']

    # Validate the input
    if not re.match(r"^(\d+)(,\s*\d+)*$", data):
        return jsonify(error="Invalid input. Please enter comma-separated integers only.")

    gen01 = [int(x) for x in data.split(',')]
    print("I'm working!")

    semigroup = create_semigroup(gen01, 5)

    semigroup_list = []
    for element in semigroup:
        semigroup_list.append(element.number())
    
    semigroup_set = set(semigroup_list)
    semigroup_list = sorted(list(semigroup_set))
    semigroup_list = semigroup_list[:20]
    print(semigroup_list)

    return jsonify(result=semigroup_list)


@app.route('/calculateFactorizationLengths', methods=['POST'])
def calculate_factorization_lengths():
    data = request.form['gen02']
    
    # Validate the input
    if not re.match(r"^(\d+)(,\s*\d+)*$", data):
        return jsonify(error="Invalid input. Please enter comma-separated integers only.")
    gen02 = [int(x) for x in data.split(',')]

    element_data = request.form['element01']

    # Validate the single integer input
    if not re.match(r"^\d+$", element_data):
        return jsonify(error="Invalid input. Please enter a valid integer.")
    
    element = int(element_data)
    semigroup2 = create_semigroup(gen02, N)
    single_element_invariant_list = create_invariants_for_single_element(semigroup2, element, gen02)
    
    return jsonify(result2=single_element_invariant_list)



@app.route('/createSecondFrobeniusGraph', methods=['POST'])
def create_second_frobenuis_graph():
    data = request.form['gen03']

    # Validate the input
    if not re.match(r"^(\d+)(,\s*\d+)*$", data):
        return jsonify(error="Invalid input. Please enter comma-separated integers only.")
    gen03 = [int(x) for x in data.split(',')]

    semigroup3 = create_semigroup(gen03, N)
    length_counts = calc_num_of_elements_of_len_k(semigroup3, gen03, N)
    df = create_factorization_fig(N, length_counts)
    

    labels = list(df.index)
    values = list(df['num'])

    data_for_chartjs = {
        "labels": labels,
        "datasets": [{
            "label": "Sample Data",
            "data": values,
            "fill": False,
            "borderColor": "rgb(75, 192, 192)"
        }]
    }

    print(data_for_chartjs)

    return jsonify(data_for_chartjs)









@app.route('/semigroups', methods=['GET', 'POST'])
def semigroups():
    example_0 = [3, 5, 6, 8, 9, 10, 11, 12, 13, 14]

    form1 = GeneratorForm1()
    form2 = GeneratorForm2()
    form3 = GeneratorForm3()

    global gen1
    global gen2
    global gen3
    single_element = 6
    print(f'Initial gen1: {gen1}, gen2: {gen2}, gen3: {gen3}')

    # Create the initial session value for gen1 and gen2
    session['gen1'] = ', '.join(str(x) for x in gen1)
    session['gen2'] = ', '.join(str(x) for x in gen2)
    session['gen3'] = ', '.join(str(x) for x in gen3)
    session['single_element'] = single_element

    if form1.validate_on_submit():
        gen1_str = form1.generators1.data
        gen1 = sorted([int(gen) for gen in gen1_str.split(",")])
        print(f'gen1 form submission {gen1} and gen2 is {gen2}')
        session['gen1'] = gen1_str

    if form2.validate_on_submit():
        gen2_str = form2.generators2.data
        gen2 = sorted([int(gen) for gen in gen2_str.split(",")])
        print(f'gen2 form submission {gen2} and gen1 is {gen1}')
        session['gen2'] = gen2_str

    if form3.validate_on_submit():
        single_element = form3.single_element.data
        gen3_str = form3.generators3.data
        gen3 = sorted([int(gen) for gen in gen3_str.split(",")])
        print(f'gen3 form submission {gen3} and gen1 is {gen1}')
        session['gen3'] = gen3_str
        session['single_element'] = single_element

    semigroup1 = create_semigroup(gen1, N)
    semigroup2 = create_semigroup(gen2, N)
    semigroup3 = create_semigroup(gen3, N)
    example_1 = create_example_1(semigroup1)
    single_element_invariant_list = create_invariants_for_single_element(
        semigroup3, single_element, gen3)
    invariant_dict = create_invariants(semigroup2, gen2)
    length_counts = calc_num_of_elements_of_len_k(semigroup2, gen2, N)
    graphjson = create_factorization_fig(N, length_counts)

    return render_template('semigroups.html',
                           example_0=example_0,
                           form1=form1,
                           example_1=example_1,
                           form2=form2,
                           form3=form3,
                           graphJSON=graphjson,
                           invariant_dict=invariant_dict,
                           list=single_element_invariant_list
                           )


if __name__ == '__main__':
    app.run(debug=True)
