# -*- coding: utf-8 -*-
"""

@author: Kerstin Scharinger
"""

import requests
import pandas as pd
import csv
import os
import Functions_Utils
import Functions_FilesAndFolders
from Functions import globVar

########################################################################################################################
#                                            --------INFO--------
# Once you have an API key, you can start making calls. The API key is a query parameter for every endpoint that you call,
# so you have to append it to your call like this for example:
# https://simfin.com/api/v1/info/find-id/ticker/AAPL?api-key=YOUR_API_KEY
# Doku-Command: https://simfin.com/api/v1/info/find-id/ticker/{tickerStr}
########################################################################################################################
# Auskommantieren: Strg + /

#=======================================================================================================================
api_key = "odiwzMBrFtZPmQDxuPnrTCPo2qhjbljn"
#=======================================================================================================================
# Script name, path, ...
filePath = os.path.realpath(__file__)
fileName = os.path.relpath(__file__)
fileDir = os.path.dirname(filePath)

########################################################################################################################
""" Get the names, SimIds and tickers of all companies contained in the SimFin database and store them in a csv file """
########################################################################################################################

def getAllCompanies():
    allCompanies_url = f"https://simfin.com/api/v1/info/all-entities?api-key={api_key}"
    allCompanies_req = requests.get(allCompanies_url)
    allCompanies = allCompanies_req.json()
    # print (allCompanies)
    # for i in allCompanies:
    # print (i)
    return (allCompanies)

def getAllCompaniesToCSV(fileName):
    # ------------------------------------------------------------------------------------------------------------------
    """ Write to excel file """
    # Arguments:
    #       dataList: [[row1],[row2]]
    # ------------------------------------------------------------------------------------------------------------------
    def writeIdentityToCSVfile(dataList, fileName):
        row = dataList
        with open(fileName + '.csv', 'a', newline='') as csvFile:           # newline -> no empty lines between entrys
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()

    for company in getAllCompanies():
        companyIdentity = [company["name"], company["simId"], company["ticker"]]
        writeIdentityToCSVfile(companyIdentity, fileName)

########################################################################################################################
""" Get the Identities: names, SimIds and tickers out of the csv and save the data in a Dictionary """
########################################################################################################################
def getCompanyIdentitiesDict(fileName):
    companyIdentitiesDict = {}
    with open(fileName + ".csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            companyIdentitiesDict[row[0]] = {"simId" : row[1], "ticker" : row[2]}
    return (companyIdentitiesDict)

########################################################################################################################
""" Get list of all available statements of the company p&l (Profit and Loss), cf (Cashflow Statement), bs (Balance Sheet) """
########################################################################################################################
def checkStatementsAvailable(simId):
    companyId = simId
    allStatements_url = f"https://simfin.com/api/v1/companies/id/{companyId}/statements/list?api-key={api_key}"
    allStatements_req = requests.get(allStatements_url)
    allStatements = allStatements_req.json()
    # print (allStatements)
    #     # for i in allStatements:
    #     #     print (i)
    return (allStatements)

########################################################################################################################
""" Get rough company information and store it in a csv-file"""
########################################################################################################################
def getRoughCompanyInfos(simId):

    request_url = f'https://simfin.com/api/v1/companies/id/{simId}?api-key={api_key}'
    content = requests.get(request_url)
    data = content.json()
    print (data)
    print (data["ticker"])

    csvfileName = data["ticker"] + ".csv"
    # TODO: Create CSV files in Data_SimFin folder and an option to store the data directly in the DB
    targetFolder = os.path.join(globVar.GLOB["ISAfileDir"], "Data_SimFin")
    csvfileName = os.path.join(globVar.GLOB["ISAfileDir"], "Data_SimFin", csvfileName)
    if os.path.exists(targetFolder) != 1:
        Functions_FilesAndFolders.createNewFolder(targetFolder)
    if os.path.exists(csvfileName):
        Functions_FilesAndFolders.createNewFile(csvfileName, "csv")

    if os.path.exists(csvfileName):
        error = "CompanyInfo-csv exists already -> " + data["ticker"]
        Functions_Utils.ERROR(error, "getRoughCompanyInfos")

    else:
        for item in data.keys():
            row = [item, data[item]]

            with open(csvfileName, 'a', newline='') as csvFile:  # newline -> no empty lines between entries
                writer = csv.writer(csvFile)
                writer.writerow(row)
            csvFile.close()


########################################################################################################################
""" Get statement data """
########################################################################################################################
# Arguments:
#       simId:              SimFin-Id of the company
#       statementType:      "pl" (profit&loss), "bs" (balance sheet), "cf" (cash flow)
#       year:               year of the statemented statement
#       timePeriod:         period of the statement ("Q1", "Q2", "Q3", "Q4", "9M", "FY")
########################################################################################################################
def writeStatementDataToCSV(simId, statementType, year, timePeriod, fileName):
    request_url = f'https://simfin.com/api/v1/companies/id/{simId}/statements/standardised?stype={statementType}&fyear={year}&ptype={timePeriod}&api-key={api_key}'
    csvFilePath = os.path.join(fileDir, "Data_SimFin", fileName)
    fileName = csvFilePath + '.csv'

    if os.path.exists(fileName):
        os.remove(fileName)
    content = requests.get(request_url)
    statement_data = content.json()
    statement = {}
    print (fileName)
    print (statement_data)
    try:
        for item in statement_data["values"]:
            statement[item["standardisedName"]] = item["valueChosen"]
            row = [item["standardisedName"], item["valueChosen"]]

            with open(fileName, 'a', newline='') as csvFile:  # newline -> no empty lines between entries
                writer = csv.writer(csvFile)
                writer.writerow(row)
            csvFile.close()

        print (statement)

    except Exception as error:
        Functions_Utils.ERROR(error, "writeStatementDataToCSV -> maybe no statement data available")

########################################################################################################################
""" Get statement from csv """
########################################################################################################################
# e.g. "C:/Users/FH/Desktop/ISA/Data_SimFin/1ST SOURCE CORP_bs_2013.csv" -> Slash not Back-Slash!!!
########################################################################################################################
def readStatementDataFromCSV(filename):
    dataDict = {}
    try:
        with open(filename, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter=",")
            for line in reader:
                dataDict[line[0]] = line[1]
                print (line[0] + " : " + line[1])
                # only lines with content
                #if line[1] != "":
                    #print (line[0], line[1])
    except Exception as error:
        Functions_Utils.ERROR(error, "readStatementDataFromCSV")

    return (dataDict)

if __name__ == "__main__":
    pass