import math
import numpy
import scipy.stats

#Berekening dikte deklaag
def Calc_Dcover (maaiveld, onderkantDeklaag): #mv = maaiveld, okd = onderkant deklaag
    return max((maaiveld - onderkantDeklaag), 0.1)

#Berekening effectieve voorlandlengte
def calc_lambda(kd, c):
    return math.sqrt(kd * c)

def calc_W(lam, L): #W staat voor de effectieve voorlandlengteformule, lam = lambda
    print("Waarde van leklengte voorland/achterland: {0}".format(lam))
    print("Waarde geometrische: {0}".format(L))

    return lam * math.tanh(L / lam)


#Berekening karakteristieke leklengte voorland (spreidingslengte)
#Verwachtingswaarde is gegeven in tabel ondergrondscenario's
def calc_kar_waarde (verwachtingswaarde, Vc, percentiel):

    log_sd = math.sqrt(math.log(1.0 + math.pow(Vc,2.0)))

    log_mu = math.log(verwachtingswaarde) - 0.5 * math.pow(log_sd,2.0)

    return scipy.stats.lognorm.ppf(percentiel,s = log_sd, loc = 0.0, scale = math.exp(log_mu))




#Berekening h_exit en kwelweg

def calc_h_exit (na, nb): #'na' en 'nb' staan voor de verschillende niveaus polderpeil of maaiveldniveau
    return max(na,nb)

def calc_dH_red (mhw, h_exit, d_cover, rc):
    return max(0.01, (mhw - h_exit - (rc * d_cover)))

#Berekening verhouding kwelweglengte vs. toegestane pipelengte
#Functie
def calc_L_kwelweg_max_ratio (dist_but, l_kwelweg, maxratio):
    if l_kwelweg > (dist_but / maxratio):
        kwelw_max_ratio = dist_but / maxratio
    else:
        kwelw_max_ratio = l_kwelweg
    return kwelw_max_ratio

#Berekening Uplift en heave

def calc_r_BIT (w1,l2,w3): #Berekening van respons ter plaatse van binnenteen
    return w3 / (w1 + l2 + w3)

def calc_r_exit (r_bit, x_bit, w3): #Berekening van respons ter plaatse van uittredepunt met model 4a
    return r_bit * math.exp(-1*(x_bit/w3))

#Functie voor beschrijving van de respons van het potentiaalverloop 4a ten opzichte van de binnenteen
def calc_r_exit4a (x, rbit, L3, lam3):

    return rbit * numpy.sinh((L3 - x) / lam3) / numpy.sinh(L3 / lam3)

def calc_pot_exit (phi_p, r_exit, h_riv): #Van respons naar potentiaal
    #self.TabelRij["Polderpeil"], self.ResponsExit, self.TabelRij["WBN"]

    print("PolderPeil: {0}".format(phi_p))
    print("ResponsExit: {0}".format(r_exit))
    print("WBN: {0}".format(h_riv))

    return phi_p + r_exit * (h_riv - phi_p)

def calc_d_pot_c_u (d_cover, gamma_sat_cover, gamma_w): #Berekening grenspotentiaal
    return d_cover * (gamma_sat_cover - gamma_w) / gamma_w

def calc_Z_u (d_pot_c_u, pot_exit, h_exit): #Berekening Z-functie opbarsten
    return d_pot_c_u - (pot_exit - h_exit)

def calc_F_u (d_pot_c_u, pot_exit, h_exit,m_u): #Berekening veiligheidsfactor opbarsten
    if pot_exit <= h_exit:
        Fu = 3.00
    else:
        Fu = (d_pot_c_u/m_u) / (pot_exit - h_exit)
    return Fu

def calc_Beta_u (F_u, Bnorm): #Berekening van veiligheidsfactor naar benaderde beta voor opbarsten
    return (math.log(F_u/0.48) + (-0.27 * Bnorm)) / 0.46 #'Bnorm' is in python negatief vandaar -1*0.27

def calc_i_optredend (pot_exit, h_exit, d_cover): #Berekening optreden heave gradient
    return (pot_exit - h_exit) / d_cover

def calc_Z_h (i_c_h, i_optredend): #Berekening Z-functie heave
    return i_c_h - i_optredend

def calc_F_h (i_c_h, i_optredend,m_he): #Berekening veiligheidsfactor heave
    if i_optredend <= 0:
        F_h = 3.00
    else:
        F_h = (i_c_h/m_he) / i_optredend
    return F_h

def calc_Beta_h (F_h, Bnorm): #Berekening van veiligheidsfactor naar benaderde beta voor heave
    return (math.log(F_h/0.37) + (-0.30 * Bnorm)) / 0.48 #'Bnorm' is in python negatief vandaar -1*0.30



def calc_dH_sellmeijer_inc_calc_settings(d70, k_z, D, L, gamma_w, visc, theta, coefficient_white, d70_ref, gamma_p): #Functie voor berekening kritiek verval Sellmeijer
    "Berekening kritiek verval methode Sellmeijer"
    "bron: bijlage 3 van "
    "invoer d70 in [m]"
    "invoer k_z in [m/d]"
    "invoer D en L in [m]"
    "rolweerstandshoek theta = 37.0 grd"
    "sleepkrachtfactor n = 0.25"
    "Volumegewicht van zandkorrels onder water = 16.5 [kN/m3]"
    "Referentie d70 waarde = 2.08*10-4 [m]"
    #Omrekenen doorlatendheid van m/d naar m/s
    k = k_z / (24 * 3600)
    #Intrinsieke doorlatendheid

    k_intr = (visc / 9.81) * k
    #Berekening Fres
    Fres = coefficient_white * ((gamma_p - gamma_w) / gamma_w) * math.tan(theta * math.pi / 180.00)
    #Fres = 0.25 * ((26.0 - gamma_w) / gamma_w) * math.tan(37.0 * math.pi / 180.00)

    #Berekening Fscale
    Fscale = pow(d70/d70_ref,0.4) * d70_ref / pow(k_intr * L, (1.0/3.0))
    #Berekening Fgeometry
    if D == L:
        D = D-0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D/L,2.8) - 1.0))
    Fgeom = 0.91 * pow(D/L,totdemacht)
    return Fres * Fscale * Fgeom * L



#Inverse Functie voor berekening benodigde kwelweglengte Sellmeijer
def calc_Lben_sellmeijer(L, d70, k_z, D, gamma_w, gamma_pip, dHred, visc, theta, coefficient_white, d70_ref, gamma_p,m_p):
    "Berekening kritiek verval methode Sellmeijer"
    "bron: bijlage 3 van "
    "invoer d70 in [m]"
    "invoer k_z in [m/d]"
    "invoer D en L in [m]"
    "theta: rolweerstandshoek"
    "coefficient white: sleepkrachtfactor"
    "gamma_p: volumegewicht van zandkorrels"
    "d70_ref: referentie d70 waarde"
    "gamma_pip: de vereiste veiligheidsfactor voor piping"
    "dHred: het gereduceerde verval per uittredepuntscenario"
    "m_p: modelfactor piping"
    #Omrekenen doorlatendheid van m/d naar m/s
    k = k_z / (24 * 3600)
    #Intrinsieke doorlatendheid
    k_intr = (visc / 9.81) * k
    #Berekening Fres
    Fres = coefficient_white * ((gamma_p - gamma_w) / gamma_w) * math.tan(theta * math.pi / 180.00)
    #Berekening Fscale
    Fscale = pow(d70/d70_ref,0.4) * d70_ref / pow(k_intr * L, (1.0/3.0))
    #Berekening Fgeometry
    if D == L:
        D = D-0.001
    else:
        pass
    totdemacht = 0.04 + (0.28 / (pow(D/L,2.8) - 1.0))
    Fgeom = 0.91 * pow(D/L,totdemacht)
    return Fres * Fscale * Fgeom * L - dHred * gamma_pip * m_p


#functie voor berekening benodigde veiligheidsfactor piping conform calibration report

def calc_gamma_pip (BetaNorm, BetaDoorsnede):
    return 1.04 * math.exp(0.37 * (-1.0 * BetaDoorsnede) - 0.43 * (-1.0 * BetaNorm))

def calc_Z_p (mp, dhc, dhred):
    return (mp * dhc) - dhred

def calc_F_p (dhc, dhred,m_p):
    return (dhc/m_p) / dhred

def calc_Beta_p (F_p, Bnorm): #Berekening van veiligheidsfactor naar benaderde beta voor piping
    return (math.log(F_p/1.04) + (-0.43 * Bnorm)) / 0.37 #'Bnorm' is in python negatief vandaar -0.43


# Verwerken resultaten op berekeningsniveau
#   Minimum van faalkansen van Uplift, Heave en piping
def calc_P_f_i (Pf_u, Pf_h, Pf_p):
    return min(Pf_u, Pf_h, Pf_p)


#   Bepaal welk faalmechanisme maatgevend is
def calc_mechanisme_maatgevend(Pf_u, Pf_h, Pf_p):
    p_min = Pf_u
    mechanisme_maatgevend = "Uplift"

    if Pf_h < p_min:
        p_min = Pf_h
        mechanisme_maatgevend = "Heave"

    if Pf_p < p_min:
        mechanisme_maatgevend = "Piping"
        p_min = Pf_p

    return mechanisme_maatgevend


# Indeling in categorieen
def calc_cat_indeling (P_f_dsn, P_eis_sign, P_eis_ond, P_eis_sign_dsn, P_eis_ond_dsn):
    #Functie voor indeling in categorieen

    if P_f_dsn < 1/30.0 * P_eis_sign_dsn:
        cat = "Iv"
    elif P_f_dsn >= 1/30.0 * P_eis_sign_dsn and P_f_dsn < P_eis_sign_dsn:
        cat = "IIv"
    elif P_f_dsn >= P_eis_sign_dsn and P_f_dsn < P_eis_ond_dsn:
        cat = "IIIv"
    elif P_eis_ond_dsn <= P_f_dsn < P_eis_ond:
        cat = "IVv"
    elif P_eis_ond <= P_f_dsn < 30.0 * P_eis_ond:
        cat = "Vv"
    elif P_f_dsn >= 30.0 * P_eis_ond and P_f_dsn <= 1.000:
        cat = "VIv"
    else:
        cat = "VIIv"
    return cat

