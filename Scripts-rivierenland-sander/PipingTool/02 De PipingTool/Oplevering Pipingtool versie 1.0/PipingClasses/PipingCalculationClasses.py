from PipingUtilities import PipingCalculationUtilities
import PipingCalculationConfig
from scipy import stats as sct
import scipy.optimize as scopt
import math
import arcpy



class Uittredepunt:
    def __init__(self, uittredepuntID, tabelRij, scenarioNamesDict):

        self.UittredepuntID = uittredepuntID
        self.TabelRij = tabelRij
        self.ScenarioNamesDict = scenarioNamesDict

        if "Vaknaam" in tabelRij.keys():
            try:
                self.Vaknaam = str(int(tabelRij["Vaknaam"]))
            except:
                self.Vaknaam = str(tabelRij["Vaknaam"])
        else:
            self.Vaknaam = "-1"

        if "VakID" in tabelRij.keys():
            try:
                self.VakID = str(int(tabelRij["VakID"]))
            except:
                self.VakID = str(tabelRij["VakID"])
        else:
            self.VakID = "-1"

        self.ControleerLokaleKans()

    def ControleerLokaleKans(self):
        self.LokaleKansAanwezig = False

        for scenarioIndex in self.ScenarioNamesDict.keys():
            scenarioNaam = self.ScenarioNamesDict[scenarioIndex]

            if scenarioNaam in self.TabelRij.keys() and self.TabelRij[scenarioNaam] != None:
                self.LokaleKansAanwezig = True

        # if ("P_S1_PL" in self.TabelRij.keys() and self.TabelRij["P_S1_PL"] != None) or\
        #         ("P_S2_HL_F" in self.TabelRij.keys() and self.TabelRij["P_S2_HL_F"] != None) or\
        #         ("P_S3_HL_TZ" in self.TabelRij.keys() and self.TabelRij["P_S3_HL_TZ"] != None):
        #     self.LokaleKansAanwezig = True
        # else:
        #     self.LokaleKansAanwezig = False




class OndergrondScenario:
    def __init__(self, ondergrondscenarioID, tabelRij):
        self.OndergrondScenarioID = ondergrondscenarioID
        self.TabelRij = tabelRij

        try:
            self.Vaknaam = str(int(tabelRij["Vaknaam"]))
        except:
            self.Vaknaam = str(tabelRij["Vaknaam"])
        self.ScenarioNaam = str(tabelRij["Scenarionaam"])


'''
Combinatie van rekenlocatie en een ondergrondscenario
'''
class PipingCalculationScenario:

    def __init__(self, uittredepunt, ondergrondScenario):
        self.Uittredepunt = uittredepunt
        self.UittredepuntID = uittredepunt.UittredepuntID
        self.OndergrondScenario = ondergrondScenario

        #   Merge dictionaries

        self.TabelRij = dict()
        for fieldName in self.Uittredepunt.TabelRij.keys():
            if not fieldName in self.TabelRij.keys():
                self.TabelRij[fieldName] = self.Uittredepunt.TabelRij[fieldName]

        for fieldName in self.OndergrondScenario.TabelRij.keys():
            if not fieldName in self.TabelRij.keys():
                self.TabelRij[fieldName] = self.OndergrondScenario.TabelRij[fieldName]

        self.Scenariotype = self.TabelRij["Scenariotype"]

    def UpdateOutputProps(self, propertyNames):
        #   Loop door de gezochte properties en check of de property aanwezig is

        for propName in propertyNames:
            if hasattr(self, propName):
                self.TabelRij[propName] = getattr(self, propName)


    def RunBerekening(self):
        self.BepaalLokaleKans()
        self.BerekenDeklaag()
        self.BerekenGeom()
        self.BerekenEffectieveLeklengtes()
        self.BerekenKwelweg()
        self.BerekenUpliftEnHeave()
        self.BerekenPiping()
        self.VerwerkResultatenBerekeningen()


    def BepaalLokaleKans(self):

        #   In principe is de lokale kans gelijk aan de kans op vakniveau
        self.LokaleKans = 0
        self.GlobaalLokaal = "Globaal"

        if self.Uittredepunt.LokaleKansAanwezig == False:
            #   Geen enkele scenario is lokaal aangepast, de kans van het vak wordt overgenomen
            self.LokaleKans = self.TabelRij["Scenariokans_vak"]

        else:
            #   Deze kans kan echter 'overruled' worden
            #   Eventueel uit te breiden met meer scenario's

            #   Loop door scenario's en kijk of er een lokale kans ingevuld is voor dit scenario

            for scenarioIndex in self.Uittredepunt.ScenarioNamesDict.keys():
                scenarioNaam = self.Uittredepunt.ScenarioNamesDict[scenarioIndex]

                if self.TabelRij["Scenarionaam"] == scenarioNaam and self.TabelRij[scenarioNaam] != None:
                    self.LokaleKans = self.TabelRij[scenarioNaam]
                    self.GlobaalLokaal = "Lokaal"

            # if "S1" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S1_PL"] != None:
            #     self.LokaleKans = self.TabelRij["P_S1_PL"]
            # elif "S2" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S2_HL_F"] != None:
            #     self.LokaleKans = self.TabelRij["P_S2_HL_F"]
            # elif "S3" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S3_HL_TZ"] != None:
            #     self.LokaleKans = self.TabelRij["P_S3_HL_TZ"]


    def BerekenDeklaag(self):
        #   In eerste instantie wordt de top van het zand opgehaald uit tabel met ondergrondscenario's

        self.TopZandVoorBerekening = -9999

        if self.Uittredepunt.LokaleKansAanwezig == False:
            #   Afkomstig uit tabel ondergrondscenario's
            self.TopZandVoorBerekening = self.TabelRij["TopZand"]
        else:
            #   Deze waarde kan 'overruled' worden in geval een lokale scneariokans en top van Pleistoceen en Holoceen zand ingevuld zijn

            if "S1" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S1_PL"] > 0 and self.TabelRij["TopPleistoceenZand"] != None:
                self.TopZandVoorBerekening = self.TabelRij["TopPleistoceenZand"]
            elif (("S2" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S2_HL_F"] > 0) or ("S3" in self.TabelRij["Scenarionaam"] and self.TabelRij["P_S3_HL_TZ"] > 0)) and self.TabelRij["TopHoloceenZand"] != None:
                self.TopZandVoorBerekening = self.TabelRij["TopHoloceenZand"]


        self.DikteDeklaag = PipingCalculationUtilities.Calc_Dcover(self.TabelRij["Bodemhoogte"], self.TopZandVoorBerekening)

        #self.DikteDeklaag = PipingCalculationUtilities.Calc_Dcover(self.TabelRij["Bodemhoogte"],self.TopZandVoorBerekening)

    def BerekenGeom(self):
        self.GeometrischeVoorlandLengte = self.TabelRij["GeometrischeKwelweglengte"] - self.TabelRij["AfstandBuitenteen"]
        self.DijkzateLengte = self.TabelRij["AfstandBuitenteen"] - self.TabelRij["AfstandBinnenteen"]
        self.GeometrischeAchterlandLengte = self.TabelRij["GeometrischeAchterlandLengte"]

    def BerekenEffectieveLeklengtes(self):
        #   Bereken leklengte voorland en achterland

        #   Input leklengte voorland kan gegeven zijn vanuit uittredepunten (afgeleid uit geohydrologisch model) dan wel
        #   uit analytische formules. In het laatste geval wordt deze parameter uitgelezen uit de tabel met ondergrondscenario's

        self.LeklengteAchterland = self.TabelRij["Spreidingslengte_achterland"]

        #   Bereken Leklengte voorland

        if PipingCalculationConfig.rekenmethodiekLeklengte == "Analytisch":
            #   Lees leklengte voorland en achterland uit Ondergrondscenario's
            self.LeklengteVoorland = self.TabelRij["Spreidingslengte_voorland"]
        else:
            self.LeklengteVoorland = self.TabelRij["DIST_spreidingslengte"] - self.TabelRij["AfstandBuitenteen"]

        #   Optie om te switchen tussen aanwezige of karakteristieke waarde LeklengteVoorland

        if PipingCalculationConfig.KarkSpreidinglengteVoorland == "Ja":
            variatieCoefficientSpreidinglengte = PipingCalculationConfig.VCSpreidingslengteVoorland
            percentielWaardeSpreidinglengte = PipingCalculationConfig.PercentielSpreidingslengteVoorland

            self.KarakteristiekeWaardeLekLengteVoorland = PipingCalculationUtilities.calc_kar_waarde(
                self.LeklengteVoorland, variatieCoefficientSpreidinglengte, percentielWaardeSpreidinglengte)
            self.RekenwaardeLeklengteVoorland = self.KarakteristiekeWaardeLekLengteVoorland

            #   Also write value of LekLengteVoorland (Karakteristiek of originele waarde uit Analytische methode dan wel geohydrologisch model)


            if self.KarakteristiekeWaardeLekLengteVoorland == 0:
                self.KarakteristiekeWaardeLekLengteVoorland = 0.01

            print("Berekening voorland")
            self.EffectieveVoorlandLengte = PipingCalculationUtilities.calc_W(
                self.KarakteristiekeWaardeLekLengteVoorland, self.GeometrischeVoorlandLengte)

            print("Effectieve voorlandlengte: {0}".format(self.EffectieveVoorlandLengte))
        else:
            print("Berekening voorland")

            if self.LeklengteVoorland == 0:
                self.LeklengteVoorland = 0.01

            self.EffectieveVoorlandLengte = PipingCalculationUtilities.calc_W(self.LeklengteVoorland,
                                                                              self.GeometrischeVoorlandLengte)

            print("Effectieve voorlandlengte: {0}".format(self.EffectieveVoorlandLengte))

            self.RekenwaardeLeklengteVoorland = self.LeklengteVoorland

        #   Stijghoogte wordt berekend met een reeks functies, dan wel uitgelezen uit een geohydrologisch model
        if PipingCalculationConfig.rekenmethodiekLeklengte == "Analytisch":
            #   Bereken Weerstand_C3_achterland

            grens_dik_dun = PipingCalculationConfig.grensDikte
            k_waarde_dik = PipingCalculationConfig.doorlatendheidDikkeDeklaag
            k_waarde_dun = PipingCalculationConfig.doorlatendheidDunneDeklaag

            if self.TabelRij["Weerstand_C3_achterland_handmatig"] != None and self.TabelRij["Weerstand_C3_achterland_handmatig"] != "":
                self.Weerstand_C3_achterland = self.TabelRij["Weerstand_C3_achterland_handmatig"]
            else:
                self.Weerstand_C3_achterland = self.TabelRij["Weerstand_C3_achterland"]

            #   Haal de geschatte waarde van D_Cover op uit TabelOndergrondscenarios
            #   Deze waarde wordt dus niet aangepast aan een lokaal afwijkende top van het zand

            dikteDeklaagVoorVak = self.TabelRij["D_cover_vak"]

            #   Weerstand_C1_voorland is een parameter met een constante waarde

            self.Weerstand_C1_voorland = self.TabelRij["Weerstand_C1_voorland"]  # Zal afgeleid worden uit Ondergrondscenario's

            #   Bereken weerstand zandpakket en effectieve voorlandlengte op basis van leklengte en geometrische voorlandlengte

            print("Berekening achterland")

            if self.LeklengteAchterland == 0:
                self.StijghoogteWaterVoerendPakketBijUittredepunt = self.TabelRij["Polderpeil"]
            else:

                self.EffectieveAchterlandLengte = PipingCalculationUtilities.calc_W(self.LeklengteAchterland, self.GeometrischeAchterlandLengte)

                #   Berekening respons binnendijks en stijghoogte

                self.ResponsBinnenteen = PipingCalculationUtilities.calc_r_BIT(self.EffectieveVoorlandLengte, self.DijkzateLengte, self.EffectieveAchterlandLengte)
                self.ResponsExit = PipingCalculationUtilities.calc_r_exit4a(self.TabelRij["AfstandBinnenteen"], self.ResponsBinnenteen, self.GeometrischeAchterlandLengte, self.LeklengteAchterland)
                self.StijghoogteWaterVoerendPakketBijUittredepunt = PipingCalculationUtilities.calc_pot_exit(self.TabelRij["Polderpeil"], self.ResponsExit, self.TabelRij["WBN"])

        else:
            #   Leklengte is gegeven vanuit geografische input (bijv. vanuit geohydrologisch model)

            self.StijghoogteWaterVoerendPakketBijUittredepunt = self.TabelRij["Stijghoogte_GeohydrologischModel"]


    def BerekenKwelweg(self):

        self.FreatischNiveauUittredepunt = PipingCalculationUtilities.calc_h_exit(self.TabelRij["Bodemhoogte"], self.TabelRij["Polderpeil"])
        self.LengteKwelweg = self.EffectieveVoorlandLengte + self.TabelRij["AfstandBuitenteen"]

        #   ToDo: waarom None waardes?
        self.GereduceerdOptredendVerval = PipingCalculationUtilities.calc_dH_red(self.TabelRij["WBN"], self.FreatischNiveauUittredepunt, self.DikteDeklaag, PipingCalculationConfig.rc)
        self.OptredendVerval = self.TabelRij["WBN"] - self.FreatischNiveauUittredepunt

        #   Benodigde kwelweglengte berekenen met solver

        #   Berekening gamma_pip

        #self.VeiligheidsFactorPiping = PipingCalculationUtilities.calc_gamma_pip(PipingCalculationConfig.Beta_norm, PipingCalculationConfig.Beta_eis_ond_dsn)

        #TODO: wat is het verschil tussen Beta_norm en beta_eis_dsn

        beta_norm = float(PipingCalculationConfig.Get_Beta_norm())
        beta_eis_dsn = float(PipingCalculationConfig.Get_Beta_dsn())
        self.VeiligheidsFactorPiping =  PipingCalculationUtilities.calc_gamma_pip(beta_norm,beta_eis_dsn)

        #   Inverse berekening op basis van GereduceerdOptredendVerval

        self.BenodigdeKwelweglengte = -9999
        try:
            solverOutput = scopt.fsolve(PipingCalculationUtilities.calc_Lben_sellmeijer, 20.0, args=(self.TabelRij["D70"],self.TabelRij["k_WVP"],
                                                                                                     self.TabelRij["Dikte_WVP"],PipingCalculationConfig.gamma_w, self.VeiligheidsFactorPiping, self.GereduceerdOptredendVerval,
                                                                                                     PipingCalculationConfig.visc,PipingCalculationConfig.theta,PipingCalculationConfig.coefficient_white,PipingCalculationConfig.d70_ref,PipingCalculationConfig.gamma_p,PipingCalculationConfig.m_p))


            if len(solverOutput) > 0:
                self.BenodigdeKwelweglengte = solverOutput[0]
        except:
            self.BenodigdeKwelweglengte = -9999
            pass


        #   Bereken tekort aan kwelweglengte

        self.KwelweglengteTekort = self.BenodigdeKwelweglengte - self.LengteKwelweg

        self.RatioPipeLengteKwelweglengte = self.TabelRij["AfstandBuitenteen"] / self.LengteKwelweg
        self.LengteKwelwegBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_L_kwelweg_max_ratio(self.TabelRij["AfstandBuitenteen"], self.LengteKwelweg, PipingCalculationConfig.MaxRatioPipeLengteKwelweglengte)
        self.KritiekePipelengte = self.BenodigdeKwelweglengte * PipingCalculationConfig.MaxRatioPipeLengteKwelweglengte
        self.FactorKritiekePipelengte = PipingCalculationConfig.MaxRatioPipeLengteKwelweglengte
        self.AfstandGrensKritiekePipelengte = self.TabelRij["AfstandGrensKritiekePipelengte"]
        self.KritiekePipelengteTekort = self.KritiekePipelengte - self.AfstandGrensKritiekePipelengte
        self.BenodigdeDijkbasisFactor = self.BenodigdeKwelweglengte/self.TabelRij["AfstandBuitenteen"]

        self.DijkbasisOordeel = "Voldoet niet"

        if self.KritiekePipelengte < self.TabelRij["AfstandGrensKritiekePipelengte"]:
            self.DijkbasisOordeel = "Voldoet"




    def BerekenUpliftEnHeave(self):

        #   Berekeningen Uplift

        #   Beta_norm verplaatsen naar constructor
        beta_norm = PipingCalculationConfig.Get_Beta_norm()

        self.KritiekStijghoogteVerschilOpbarsten = PipingCalculationUtilities.calc_d_pot_c_u(self.DikteDeklaag, self.TabelRij["gamma_sat_cover_vak"], PipingCalculationConfig.gamma_w)
        self.GrensToestandOpbarsten = PipingCalculationUtilities.calc_Z_u(self.KritiekStijghoogteVerschilOpbarsten, self.StijghoogteWaterVoerendPakketBijUittredepunt, self.FreatischNiveauUittredepunt)
        self.StabiliteitsFactorOpbarsten = PipingCalculationUtilities.calc_F_u(self.KritiekStijghoogteVerschilOpbarsten, self.StijghoogteWaterVoerendPakketBijUittredepunt, self.FreatischNiveauUittredepunt,PipingCalculationConfig.m_u)
        self.BetrouwbaarheidsIndexOpbarsten = PipingCalculationUtilities.calc_Beta_u(self.StabiliteitsFactorOpbarsten, beta_norm)
        self.ScenarioFaalkansOpbarsten = sct.norm.cdf(-1 * self.BetrouwbaarheidsIndexOpbarsten)

        #   Berekeningen Heave
        self.OptredendeHeaveGradient = PipingCalculationUtilities.calc_i_optredend(self.StijghoogteWaterVoerendPakketBijUittredepunt, self.FreatischNiveauUittredepunt, self.DikteDeklaag)

        self.GrensToestandHeave = PipingCalculationUtilities.calc_Z_h(PipingCalculationConfig.i_c_h, self.OptredendeHeaveGradient)
        self.StabiliteitsFactorHeave = PipingCalculationUtilities.calc_F_h(PipingCalculationConfig.i_c_h, self.OptredendeHeaveGradient, PipingCalculationConfig.m_he)
        self.BetrouwbaarheidsIndexHeave = PipingCalculationUtilities.calc_Beta_h(self.StabiliteitsFactorHeave, beta_norm)
        self.ScenarioFaalkansHeave = sct.norm.cdf(-1 * self.BetrouwbaarheidsIndexHeave)


    def BerekenPiping(self):


        #   Pass additional calculation settings to Sellmeijer calculation
        self.KritiekVervalPipingSellmeijer = PipingCalculationUtilities.calc_dH_sellmeijer_inc_calc_settings(self.TabelRij["D70"], self.TabelRij["k_WVP"],
                                                                                                             self.TabelRij["Dikte_WVP"], self.LengteKwelweg,
                                                                                                             PipingCalculationConfig.gamma_w, PipingCalculationConfig.visc, PipingCalculationConfig.theta,
                                                                                                             PipingCalculationConfig.coefficient_white, PipingCalculationConfig.d70_ref, PipingCalculationConfig.gamma_p)


        self.GrensToestandPiping = PipingCalculationUtilities.calc_Z_p(PipingCalculationConfig.m_p, self.KritiekVervalPipingSellmeijer, self.GereduceerdOptredendVerval)
        self.StabiliteitsFactorPiping = PipingCalculationUtilities.calc_F_p(self.KritiekVervalPipingSellmeijer, self.GereduceerdOptredendVerval, PipingCalculationConfig.m_p)

        beta_norm = PipingCalculationConfig.Get_Beta_norm()


        self.BetrouwbaarheidsIndexPiping = PipingCalculationUtilities.calc_Beta_p(self.StabiliteitsFactorPiping,beta_norm)
        self.ScenarioFaalkansPiping = sct.norm.cdf(-1 * self.BetrouwbaarheidsIndexPiping)



    def VerwerkResultatenBerekeningen(self):

        #   Bepaal minimum faalkans over 3 mechanismen
        self.FaalkansScenario = PipingCalculationUtilities.calc_P_f_i(self.ScenarioFaalkansOpbarsten, self.ScenarioFaalkansHeave, self.ScenarioFaalkansPiping)

        #   Bereken maximun van de beta's voor piping, heave en opbarsten - deze is gekoppeld aan de minimum faalkans

        self.MaximumWaardeBetaScenario = max(self.BetrouwbaarheidsIndexPiping, self.BetrouwbaarheidsIndexHeave, self.BetrouwbaarheidsIndexOpbarsten)

        #   Bepaal bij welk mechanisme deze minimum faalkans hoort
        self.BepalendMechanismeFaalkansScenario = PipingCalculationUtilities.calc_mechanisme_maatgevend(self.ScenarioFaalkansOpbarsten, self.ScenarioFaalkansHeave, self.ScenarioFaalkansPiping)

        #   Vermenigvuldig de faalkans met de kans op voorkomen van het scenario
        #   In de aggregatie (per uittredepunt) worden deze faalkansen bij elkaar opgeteld
        self.FaalkansxScenarioKans = self.FaalkansScenario * self.LokaleKans

        self.KritiekVervalPipingSellmeijerBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_dH_sellmeijer_inc_calc_settings(self.TabelRij["D70"], self.TabelRij["k_WVP"], self.TabelRij["Dikte_WVP"],
                                                                                                                                   PipingCalculationConfig.MaxRatioPipeLengteKwelweglengte, PipingCalculationConfig.gamma_w,
                                                                                                                                   PipingCalculationConfig.visc, PipingCalculationConfig.theta,PipingCalculationConfig.coefficient_white,
                                                                                                                                   PipingCalculationConfig.d70_ref,PipingCalculationConfig.gamma_p)

        #   Toevoegen berekening benodigde kwelweglengte (met solver)

        beta_norm = PipingCalculationConfig.Get_Beta_norm()
        self.StabiliteitsFactorPipingBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_F_p(self.KritiekVervalPipingSellmeijerBijMaxRatioPipeKwelweg, self.GereduceerdOptredendVerval,PipingCalculationConfig.m_p)
        #self.BetrouwbaarheidsIndexPipingBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_Beta_p(self.StabiliteitsFactorPipingBijMaxRatioPipeKwelweg, PipingCalculationConfig.Beta_norm)
        self.BetrouwbaarheidsIndexPipingBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_Beta_p(self.StabiliteitsFactorPipingBijMaxRatioPipeKwelweg, beta_norm)
        self.ScenarioFaalkansPipingBijMaxRatioPipeKwelweg = sct.norm.cdf(-1 * self.BetrouwbaarheidsIndexPipingBijMaxRatioPipeKwelweg)
        self.FaalkansScenarioBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_P_f_i(self.ScenarioFaalkansOpbarsten, self.ScenarioFaalkansHeave, self.ScenarioFaalkansPipingBijMaxRatioPipeKwelweg)
        self.BepalendMechanismeFaalkansScenarioBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_mechanisme_maatgevend(self.ScenarioFaalkansOpbarsten, self.ScenarioFaalkansHeave, self.ScenarioFaalkansPipingBijMaxRatioPipeKwelweg)
        self.ProductFaalkansScenarioBijMaxRatioPipeKwelweg = self.FaalkansScenarioBijMaxRatioPipeKwelweg * self.LokaleKans


class PipingCalculationResultaat:

    def __init__(self, uittredepunt, pipingCalculationScenarios):
        self.Uittredepunt = uittredepunt
        self.PipingCalculationScenarios = pipingCalculationScenarios
        self.TabelRij = dict()
        self.TabelRij["UittredePointShape"] = self.Uittredepunt.TabelRij["UittredePointShape"]
        self.TabelRij["UittredepuntenID"] = self.Uittredepunt.UittredepuntID
        self.TabelRij["Vaknaam"] = self.Uittredepunt.Vaknaam
        self.TabelRij["VakID"] = self.Uittredepunt.VakID
        self.TabelRij["AfstandGrensKritiekePipelengte"] = self.Uittredepunt.TabelRij["AfstandGrensKritiekePipelengte"]

    def UpdateOutputProps(self, propertyNames):
        #   Loop door de gezochte properties en check of de property aanwezig is

        for propName in propertyNames:
            if hasattr(self, propName):
                self.TabelRij[propName] = getattr(self, propName)


    def AggregeerResultaten(self):
        self.SomProductFaalkansScenariokans = 0

        self.MaatgevendeBenodigdeKwelweglengte = 0
        self.MaatgevendDijkbasisOordeel = "Voldoet"

        #   Loop door ondergrondscenario's en controleer of overal aan het dijkbasisoordeel wordt voldaan

        for pipingCalculationScenario in self.PipingCalculationScenarios:
            self.SomProductFaalkansScenariokans += pipingCalculationScenario.FaalkansxScenarioKans

            if pipingCalculationScenario.BenodigdeKwelweglengte > self.MaatgevendeBenodigdeKwelweglengte:
                self.MaatgevendeBenodigdeKwelweglengte = pipingCalculationScenario.BenodigdeKwelweglengte
                self.MaatgevendDijkbasisOordeel = pipingCalculationScenario.DijkbasisOordeel

        #   Bepaal het maximum van de faalkansen die bij de scenario's horen
        self.MaxFaalkansScenario = max(self.PipingCalculationScenarios, key=lambda p: p.FaalkansScenario).FaalkansScenario

        #   TODO: uitzoeken hoe BetaDoorsnedeKans, BetaMaatgevendScenario en BetaDoorsnedeEis berekend kan worden

        self.BetaDoorsnedeKans = -1*sct.norm.ppf(self.SomProductFaalkansScenariokans)
        self.BetaMaatgevendeScenario = -1*sct.norm.ppf(self.MaxFaalkansScenario)
        #self.BetaDoorsnedeEis = -1*PipingCalculationConfig.Get_Beta_norm()

        self.BetaDoorsnedeEis = -1 * PipingCalculationConfig.Get_Beta_dsn()

        #   ToDo: rekenen met ondergrens of signaleringswaarde (is een rekeninstelling)

        Pf_eis = PipingCalculationConfig.Get_Pf_dsn()

        self.FaalkansDoorsnedeEis = Pf_eis
        self.UnityCheckFaalkansDoorsnedeEis = self.SomProductFaalkansScenariokans / Pf_eis
        self.UnityCheckBetaDoorsnedeEis = self.BetaDoorsnedeEis / self.BetaDoorsnedeKans


        #self.UnityCheckDoorsnedeEis = self.SomProductFaalkansScenariokans / PipingCalculationConfig.Pf_eis_ond_dsn
        #self.UnityCheckDoorsnedeEisBijMaxRatioPipeKwelweg = self.FaalkansScenarioBijMaxRatioPipeKwelweg / PipingCalculationConfig.Pf_eis_ond_dsn
        self.CategorieToetsoordeel = PipingCalculationUtilities.calc_cat_indeling(self.SomProductFaalkansScenariokans, PipingCalculationConfig.GetPf_eis_sign(), PipingCalculationConfig.GetPf_eis_ond(),
                                                                                  PipingCalculationConfig.GetPf_eis_sign_dsn(), PipingCalculationConfig.GetPf_eis_ond_dsn())

        #   Bepaal maximale effectieve en benodigde kwelweglengte
        self.MaximaleEffectieveKwelweglengte = max(self.PipingCalculationScenarios, key=lambda p: p.LengteKwelweg).LengteKwelweg
        self.MaxBenodigdeKwelweglengte = max(self.PipingCalculationScenarios, key=lambda p: p.BenodigdeKwelweglengte).BenodigdeKwelweglengte
        self.MaximaalKwelweglengteTekort = max(self.PipingCalculationScenarios, key=lambda p: p.KwelweglengteTekort).KwelweglengteTekort


        #   Bepaal maximum van kritieke pipelengte
        self.MaximaleKritiekePipelengte = max(self.PipingCalculationScenarios, key=lambda p: p.KritiekePipelengte).KritiekePipelengte
        self.MaximaleKritiekePipelengteTekort = max(self.PipingCalculationScenarios, key=lambda p: p.KritiekePipelengteTekort).KritiekePipelengteTekort


        #
        #self.FaalkansScenarioBijMaxRatioPipeKwelweg = max(self.PipingCalculationScenarios, key=lambda p: p.FaalkansScenarioBijMaxRatioPipeKwelweg).FaalkansScenarioBijMaxRatioPipeKwelweg
        #self.LengteKwelwegBijMaxRatioPipeKwelweg = max(self.PipingCalculationScenarios, key=lambda p: p.LengteKwelwegBijMaxRatioPipeKwelweg).LengteKwelwegBijMaxRatioPipeKwelweg


        #self.CategorieToetsoordeelBijMaxRatioPipeKwelweg = PipingCalculationUtilities.calc_cat_indeling(self.FaalkansScenarioBijMaxRatioPipeKwelweg,PipingCalculationConfig.Pf_eis_sign,
        #                                                                          PipingCalculationConfig.Pf_eis_ond,PipingCalculationConfig.Pf_eis_sign_dsn,PipingCalculationConfig.Pf_eis_ond_dsn)

        self.Eindoordeel = self.CategorieToetsoordeel

        if self.MaatgevendDijkbasisOordeel == "Voldoet niet":
            self.Eindoordeel = "Voldoet niet vanwege dijkbasisregel"


        #res['UnityCheckDoorsnedeEisBijMaxRatioPipeKwelweg'] = res['P_f_dsn_max_ratio'] / Pf_eis_ond_dsn







        # res['Categorie'] = np.vectorize(calc_cat_indeling)(res['P_f_dsn'], Pf_eis_sign, Pf_eis_ond, Pf_eis_sign_dsn,
        #                                                    Pf_eis_ond_dsn)
        # res['Categorie_max_ratio'] = np.vectorize(calc_cat_indeling)(res['P_f_dsn_max_ratio'], Pf_eis_sign, Pf_eis_ond,
        #                                                              Pf_eis_sign_dsn, Pf_eis_ond_dsn)
        #
        # # bepaal afstand tot de doorsnede eis van de norm
        # res['UnityCheckDoorsnedeEis'] = res['P_f_dsn'] / Pf_eis_ond_dsn
        # res['UnityCheckDoorsnedeEisBijMaxRatioPipeKwelweg'] = res['P_f_dsn_max_ratio'] / Pf_eis_ond_dsn



#class PipingCalculationPoint