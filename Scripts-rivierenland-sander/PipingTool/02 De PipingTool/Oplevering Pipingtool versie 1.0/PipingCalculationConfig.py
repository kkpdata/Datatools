import scipy.stats as sct

#   Constante inputs voor piping berekening

#   Instellingen Sellmeijer

visc = 0.00000133 # Kinematische viscositeit waarmee de intrinsieke doorlatendheid wordt bepaald. Standaard waarde is gebaseerd op grondwater van 10 graden celsius.
theta = 37.0   # Rolweerstandshoek van de zandkorrels
coefficient_white = 0.25 # Coefficient van White
d70_ref = 0.000208 # gemiddelde d70 in de kleine schaalproeven
gamma_p = 16.5    # (schijnbaar) volumegewicht van de zandkorrels onder water

#Functie voor berekening kritiek verval Sellmeijer

#   Modelfactoren

m_p = 1.00
m_u = 1.00
m_he = 1.00

#   Constante voor h_exit en kwelweg
rc = 0.30
MaxRatioPipeLengteKwelweglengte = 0.5 # Moet aan te passen zijn

# Constanten
gamma_w = 9.81  # volumiek gewicht van water in kN/m3
i_c_h = 0.300  # kritieke gradient heave

#Lengte-effect
w = 0.24 # Moet aan te passen zijn. Dit is de waarde voor TiWa + GoWa tezamen (dijktraject 43-6)
L = 46859.32 # Moet aan te passen zijn. Dit is de waarde voor TiWa + GoWa tezamen (dijktraject 43-6)
a_l = 0.9 # Mechanismegevoelige fractie van de dijktrajectlengte
b_l = 300  # Lengte van het dijktraject zoals vastgelegd in Bijlage II van de Waterweg [m]
#N_dsn = 1 + (a_l * L) / b_l


#   Normeringen
Return_eis_selectie = "Ondergrenswaarde"
Return_eis_sign = 30000.0
Return_eis_ond = 10000.0

#   Spreidingslengte voorland
KarkSpreidinglengteVoorland = "Ja"
VCSpreidingslengteVoorland = 0.1
PercentielSpreidingslengteVoorland = 0.05

def Get_N_dsn():
    return 1 + (a_l * L) / b_l

def Get_Pf_eis():
    if Return_eis_selectie == "Signaleringswaarde":
        return 1.0/Return_eis_sign
    elif Return_eis_selectie == "Ondergrenswaarde":
        return 1.0/Return_eis_ond

def Get_Pf_dsn():
    Pf_eis = Get_Pf_eis()
    N_dsn = Get_N_dsn()
    return (w * Pf_eis) / N_dsn

def Get_Beta_dsn():
    Pf_eis_dsn = Get_Pf_dsn()
    return sct.norm.ppf(Pf_eis_dsn)

def Get_Beta_norm():
    Pf_eis = Get_Pf_eis()
    return sct.norm.ppf(Pf_eis)

#   Moet aan te passen zijn (wordt nu alleen gebruikt voor bepaling categorie-indeling)
#   Moet ook gebruikt kunnen worden in toetsing van de faalkans

def GetPf_eis_sign():
    return 1.0/Return_eis_sign

#   Deze wordt nu altijd gebruikt in de toetsing van de faalkans
def GetPf_eis_ond():
    return 1.0/Return_eis_ond # Moet aan te passen zijn

#signaleringwaarde van de norm
def GetPf_eis_sign_dsn():
    return (w *  GetPf_eis_sign()) / Get_N_dsn()

#Ondergrens van de norm
def GetPf_eis_ond_dsn():
    return (w * GetPf_eis_ond()) / Get_N_dsn()

def Beta_eis_ond_dsn():
    return sct.norm.ppf(GetPf_eis_ond_dsn())
#
# #Welke norm gebruiken we?
Pf_norm = GetPf_eis_ond()


#   Instellingen voor bepaling van de weerstanden en leklengtes
#   Doorlatendheden zijn in m/dag

rekenmethodiekLeklengte = "Analytisch"
doorlatendheidDunneDeklaag = 0.1
doorlatendheidDikkeDeklaag = 0.01
grensDikte = 1.5