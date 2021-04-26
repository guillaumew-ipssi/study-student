from flask import Flask, jsonify
from flask import render_template
from flask import request
import pandas as pd
import matplotlib.pyplot as plt
import math

app = Flask(__name__)

df = pd.read_csv("student.csv")
df_dum = pd.get_dummies(df)
df['note_moyenne'] = ((df['G1'] + df['G2'] + df['G3'])/3).round(2)
df['consommation'] = ((df['Dalc'] + df['Walc'])).round(2)

# Home page route
@app.route('/')
def hello_world():
	nb_student = len(df)
	ages = show_ages()
	sex = show_sex()
	absenceage = show_absences_by_age()
	higher = show_pourcent_higher()
	absences = show_absences()
	conso = show_conso()
	result_school = show_school_results()
	alcool_out = show_alcool_out()
	absences_conso = show_absences_conso()
	nb_absences = show_nb_absences()

	return render_template('home.html', ages=ages, nb_student=nb_student, sex=sex, absenceage=absenceage, higher=higher, absences=absences, conso=conso, result_school=result_school, alcool_out=alcool_out, absences_conso=absences_conso, nb_absences=nb_absences)

# Show the form route
@app.route('/show/test')
def show_test():
	return render_template('test.html')

# Process the form and generate the results
@app.route('/trait/test', methods=["POST"])
def trait_test():
    prenom = request.form['prenom']
    sex = request.form['sex']
    age = request.form['age']

    #For the first informations of user (percentage, etc...)
    percentage_age = len(df.loc[df['age'] == int(age) ]) / len(df) * 100
    df_age_sex = df.loc[df['age'] == int(age)]
    percentage_age_sex = len(df_age_sex.loc[df_age_sex['sex'] == sex]) / len(df_age_sex) * 100

    df_form_sex = getDataframeToSex(sex)
    df_form = getDataframeToAge(df_form_sex, age)

	# Get the data for generate the graphic about family size of student. Data user and data average
    famsize = request.form['famsize']
    df_famsize = getDataframeToFamsize(df_form, famsize)
    famsize_form = getAverageConsumption(df_famsize)
    famsize_to_compare = getAverageConsumptionToAgeWithFamsize(df, sex, famsize)

	# Get the data for generate the graphic about the parent status of student. Data user and data average
    pstatus = request.form['pstatus']
    df_pstatus = getDataframeToPstatus(df_form, pstatus)
    pstatus_form = getAverageConsumption(df_pstatus)
    pstatus_to_compare_m = getAverageConsumptionToAge(df, 'M', pstatus)
    pstatus_to_compare_f = getAverageConsumptionToAge(df, 'F', pstatus)

	# The next data to process
    activities = request.form['activities']
    internet = request.form['internet']
    Dalc = request.form['Dalc']
    Walc = request.form['Walc']

	# Send the datas to the template
    return render_template('result_test.html', prenom=prenom, sex=sex, age=age, percentage_age=percentage_age, percentage_age_sex=percentage_age_sex, famsize=famsize, 
    pstatus=pstatus, Dalc=Dalc, Walc=Walc,df_form=df_form, famsize_form=famsize_form, famsize_to_compare=famsize_to_compare, 
    pstatus_form=pstatus_form, pstatus_to_compare_m=pstatus_to_compare_m, pstatus_to_compare_f=pstatus_to_compare_f)

#########################
# Functions to the form #
#########################

# Get the average consumption alcohol for one week complete ( week and week-end ) 
def getAverageConsumption(df):
    return ((df['Walc'] + df['Dalc'])/2).mean()

# Get the average consumption alcohol for each age about the size of family
def getAverageConsumptionToAgeWithFamsize(df, sex, famsize):
    average_alcohol_age = list()

    df_sex = df.loc[df['sex'] == sex]

    for i in range(15,23):
        df_age = df_sex.loc[df_sex['age'] == i ]
        df_famsize = getDataframeToFamsize(df_age, famsize)
        average = getAverageConsumption(df_famsize)
        if math.isnan(average) :
            average = 0

        average_alcohol_age.append(average)

    return average_alcohol_age

# Get the average consumption alcohol for each age
def getAverageConsumptionToAge(df, sex, pstatus):
    average_alcohol_age = list()

    df_sex = df.loc[df['sex'] == sex]

    for i in range(15,23):
        df_age = df_sex.loc[df_sex['age'] == i ]
        df_pstatus = getDataframeToPstatus(df_age, pstatus)
        average = getAverageConsumption(df_pstatus)
        if math.isnan(average) :
            average = 0

        average_alcohol_age.append(average)

    return average_alcohol_age

# Get the dataFrame with the students according to the size family
def getDataframeToFamsize(df, famsize):
    df = df.loc[df['famsize'] == famsize]
    return df

# Get the dataFrame with the students according to the parent status
def getDataframeToPstatus(df, pstatus):
    df = df.loc[df['Pstatus'] == pstatus]
    return df

# Get the dataFrame with the students according to the sex
def getDataframeToSex(sex):
    df = pd.read_csv("student.csv")
    df_sex = df.loc[df['sex'] == sex]
    return df_sex

# Get the dataFrame with the students according to the age
def getDataframeToAge(df, age):
    if type(age) is int :
        df_age = df.loc[df['age'] == age]
    else:
        df_age = df.loc[df['age'] == int(age)]
    return df_age


###################################
# Functions to graphics home page #
###################################

def show_ages():
	ages = list(df['age'].value_counts(normalize=True).round(4) * 100)
	return ages

def show_sex():
	res_list = list()
	res_list.append(df['sex'].value_counts()['F'])
	res_list.append(df['sex'].value_counts()['M'])
	return res_list

def show_absences_by_age():
	df_absences_by_age = df.groupby(['age']).mean()
	absences_by_age = round(df_absences_by_age['absences'], 1)
	list_absences_by_age = list(absences_by_age)
	return list_absences_by_age

def show_absences():
	df_romantic = df_dum.loc[(df_dum['romantic_yes'] == 1)]
	df_romantic_no = df_dum.loc[(df_dum['romantic_no'] == 1)]
	absences_romantic = df_romantic['absences'].median()
	absences_noromantic = df_romantic_no['absences'].median()
	absences_list = list()
	absences_list.append(absences_romantic)
	absences_list.append(absences_noromantic)
	return absences_list

def show_pourcent_higher():
	df_higher_yes = df_dum.loc[(df_dum['higher_yes'] == 1)]
	percent_higher_yes = 100 * len(df_higher_yes) / len(df)
	percent_higher = round(percent_higher_yes, 1)
	return percent_higher

def show_conso():
	df_conso_by_age = df.groupby(['age']).mean()
	conso_by_age = round(df_conso_by_age['consommation'], 1)
	list_conso = list(conso_by_age)
	return list_conso


def show_school_results():
	df = pd.read_csv("student.csv")

	note_moyenne = ((df['G1'] + df['G2'] + df['G3'])/3).round(2)
	df['note_moyenne'] = note_moyenne

	df_gb = df.groupby(["Walc"])[['note_moyenne']].mean()

	res_list = list()
	for res in df_gb['note_moyenne']:
		res_list.append(res)

	return res_list


def show_alcool_out():
	df_gb = df.groupby(['goout'])[["Dalc", "Walc"]].mean()

	res_list = list()
	for res in df_gb['Dalc']:
		res_list.append(res)

	# for res in df_gb['Walc']:
	# 	res_list.append(res)

	return res_list


def show_absences_conso():
	df_gb = df.groupby(['absences'])[["Dalc"]].mean()

	res_list = list()
	for res in df_gb['Dalc']:
		res_list.append(res)

	return res_list

def show_nb_absences():
	df_gb = df.groupby(['absences']).mean()

	res_list = list()
	for res in df_gb.index:
		res_list.append(res)

	return res_list
