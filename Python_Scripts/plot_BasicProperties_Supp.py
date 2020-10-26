# Supplementary Plot --- Figure S1
# plot some basic properties of the model collection

import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np


# check whether the folder 'Benchmarking_of_numerical_ODE_integration_methods/json_files' exists
skip_indicator = 0
if os.path.exists('../../Benchmarking_of_numerical_ODE_integration_methods/json_files'):
    skip_indicator = 1

all_log_abs_tol = ['03', '06', '06', '16', '12']
all_log_rel_tol = ['03', '03', '06', '08', '12']
all_abs_tol = [r'$10^{-3}$', r'$10^{-6}$', r'$10^{-6}$', r'$10^{-16}$', r'$10^{-12}$']
all_rel_tol = [r'$10^{-3}$', r'$10^{-3}$', r'$10^{-6}$', r'$10^{-8}$', r'$10^{-12}$']

counter_Tol_0 = []
counter_Tol_1 = []
counter_Tol_2 = []
counter_Tol_3 = []
counter_Tol_4 = []
for iTolerance in range(0, len(all_log_abs_tol)):
    abs_tol = all_log_abs_tol[iTolerance]
    rel_tol = all_log_rel_tol[iTolerance]
    adams_models = []
    bdf_models = []
    counters_Adams = []
    counters_BDF = []
    for Multistep in ['Adams', 'BDF']:
        print(Multistep)
        tol_exps = []
        for tol_exp in range(-20, 10):
            tol = 10**tol_exp
            counter = 0
            total_counter = 0
            tol_str = f"{float(tol):.0e}"
            if skip_indicator == 0:
                base_dir_JWS = f"../Data/JWS_AMICI_state_trajectory_comparison/json_files_all_results_{Multistep}_{abs_tol}_{rel_tol}/json_files_{tol_str}_{tol_str}"
                base_dir_COPASI = f"../Data/BioModels_AMICI_state_trajectory_comparison/COPASI_all_results_{Multistep}_{abs_tol}_{rel_tol}/COPASI_{tol_str}_{tol_str}"
            elif skip_indicator == 1:
                base_dir_JWS = f"../../Benchmarking_of_numerical_ODE_integration_methods/json_files_all_results_{Multistep}_{abs_tol}_{rel_tol}/json_files_{tol_str}_{tol_str}"
                base_dir_COPASI = f"../../Benchmarking_of_numerical_ODE_integration_methods/COPASI_all_results_{Multistep}_{abs_tol}_{rel_tol}/COPASI_{tol_str}_{tol_str}"
            sedml_models_JWS = os.listdir(base_dir_JWS)
            sedml_models_COPASI = sorted(os.listdir(base_dir_COPASI))
            for sedml_model in sedml_models_JWS:
                sedml_dir = base_dir_JWS + "/" + sedml_model
                sbml_models = os.listdir(sedml_dir)
                for sbml_model in sbml_models:
                    sbml_dir = sedml_dir + "/" + sbml_model
                    filename = sbml_dir + "/" + "whole_error.csv"
                    df = pd.read_csv(filename, sep='\t')
                    if df['trajectories_match'][0] == True:
                        counter += 1
                        bdf_models.append(sedml_model + '_' + sbml_model)
                    total_counter += 1
            for sbml_model in sedml_models_COPASI:
                filename = base_dir_COPASI + '/' + sbml_model + "/" + "whole_error.csv"
                df = pd.read_csv(filename, sep='\t')
                if df['trajectories_match'][0] == True:
                    counter += 1
                    bdf_models.append(sbml_model)
                total_counter += 1
            print(tol_exp, counter, total_counter)
            if Multistep == 'Adams':
                tol_exps.append(tol_exp)
                counters_Adams.append(counter)
            elif Multistep == 'BDF':
                tol_exps.append(tol_exp)
                counters_BDF.append(counter)
    if iTolerance == 0:
        counter_Tol_0.append(counters_Adams)
        counter_Tol_0.append(counters_BDF)
    elif iTolerance == 1:
        counter_Tol_1.append(counters_Adams)
        counter_Tol_1.append(counters_BDF)
    elif iTolerance == 2:
        counter_Tol_2.append(counters_Adams)
        counter_Tol_2.append(counters_BDF)
    elif iTolerance == 3:
        counter_Tol_3.append(counters_Adams)
        counter_Tol_3.append(counters_BDF)
    elif iTolerance == 4:
        counter_Tol_4.append(counters_Adams)
        counter_Tol_4.append(counters_BDF)

ax = plt.axes()
ax.plot(tol_exps, counter_Tol_0[0], '-*', c='#fdae61', label=f'AM & {all_abs_tol[0]} & {all_rel_tol[0]}')
ax.plot(tol_exps, counter_Tol_0[1], '-*', c='#abd9e9', label=f'BDF & {all_abs_tol[0]} & {all_rel_tol[0]}')
ax.plot(tol_exps, counter_Tol_1[0], '-*', c='#f46d43', label=f'AM & {all_abs_tol[1]} & {all_rel_tol[1]}')
ax.plot(tol_exps, counter_Tol_1[1], '-*', c='#74add1', label=f'BDF & {all_abs_tol[1]} & {all_rel_tol[1]}')
ax.plot(tol_exps, counter_Tol_2[0], '-*', c='#d73027', label=f'AM & {all_abs_tol[2]} & {all_rel_tol[2]}')
ax.plot(tol_exps, counter_Tol_2[1], '-*', c='#4575b4', label=f'BDF & {all_abs_tol[2]} & {all_rel_tol[2]}')
ax.plot(tol_exps, counter_Tol_3[0], '-*', c='#a50026', label=f'AM & {all_abs_tol[3]} & {all_rel_tol[3]}')
ax.plot(tol_exps, counter_Tol_3[1], '-*', c='#313695', label=f'BDF & {all_abs_tol[3]} & {all_rel_tol[3]}')
ax.plot(tol_exps, counter_Tol_4[0], '-*', c='#800000', label=f'AM & {all_abs_tol[4]} & {all_rel_tol[4]}')
ax.plot(tol_exps, counter_Tol_4[1], '-*', c='#2E2D66', label=f'BDF & {all_abs_tol[4]} & {all_rel_tol[4]}')

# local properties
fontsize = 13
ax.set_ylim([-20,400])
ax.set_xticklabels(np.array(['', r'$10^{-20}$', r'$10^{-15}$', r'$10^{-10}$', r'$10^{-5}$', r'$10^{0}$', r'$10^{5}$', r'$10^{10}$']))

# dashed black line
ax.axvline(-4, -20, 400, c='black', linestyle='--')

# make top and right boxlines invisible
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# create custom legend
ax1 = plt.axes([0.15, 0.5, 0.3, 0.4])

# first column
ax1.text(0.07, 0.8, 'AM', fontsize=10)
ax1.axhline(0.72, 0.11, 0.12, c='#fdae61', marker=0)
ax1.axhline(0.72, 0.12, 0.12, c='#fdae61', marker='*')
ax1.axhline(0.72, 0.12, 0.13, c='#fdae61', marker=1)
ax1.axhline(0.62, 0.11, 0.12, c='#f46d43', marker=0)
ax1.axhline(0.62, 0.12, 0.12, c='#f46d43', marker='*')
ax1.axhline(0.62, 0.12, 0.13, c='#f46d43', marker=1)
ax1.axhline(0.52, 0.11, 0.12, c='#d73027', marker=0)
ax1.axhline(0.52, 0.12, 0.12, c='#d73027', marker='*')
ax1.axhline(0.52, 0.12, 0.13, c='#d73027', marker=1)
ax1.axhline(0.42, 0.11, 0.12, c='#a50026', marker=0)
ax1.axhline(0.42, 0.12, 0.12, c='#a50026', marker='*')
ax1.axhline(0.42, 0.12, 0.13, c='#a50026', marker=1)
ax1.axhline(0.32, 0.11, 0.12, c='#800000', marker=0)
ax1.axhline(0.32, 0.12, 0.12, c='#800000', marker='*')
ax1.axhline(0.32, 0.12, 0.13, c='#800000', marker=1)
# second column
ax1.text(0.255, 0.8, 'BDF', fontsize=10)
ax1.axhline(0.72, 0.31, 0.32, c='#abd9e9', marker=0)
ax1.axhline(0.72, 0.32, 0.32, c='#abd9e9', marker='*')
ax1.axhline(0.72, 0.32, 0.33, c='#abd9e9', marker=1)
ax1.axhline(0.62, 0.31, 0.32, c='#74add1', marker=0)
ax1.axhline(0.62, 0.32, 0.32, c='#74add1', marker='*')
ax1.axhline(0.62, 0.32, 0.33, c='#74add1', marker=1)
ax1.axhline(0.52, 0.31, 0.32, c='#4575b4', marker=0)
ax1.axhline(0.52, 0.32, 0.32, c='#4575b4', marker='*')
ax1.axhline(0.52, 0.32, 0.33, c='#4575b4', marker=1)
ax1.axhline(0.42, 0.31, 0.32, c='#313695', marker=0)
ax1.axhline(0.42, 0.32, 0.32, c='#313695', marker='*')
ax1.axhline(0.42, 0.32, 0.33, c='#313695', marker=1)
ax1.axhline(0.32, 0.31, 0.32, c='#2E2D66', marker=0)
ax1.axhline(0.32, 0.32, 0.32, c='#2E2D66', marker='*')
ax1.axhline(0.32, 0.32, 0.33, c='#2E2D66', marker=1)
# third column
ax1.text(0.475, 0.8, 'abs.tol.', fontsize=10)
ax1.text(0.5, 0.68, r'$10^{-3}$', fontsize=10)
ax1.text(0.5, 0.58, r'$10^{-6}$', fontsize=10)
ax1.text(0.5, 0.48, r'$10^{-6}$', fontsize=10)
ax1.text(0.5, 0.38, r'$10^{-16}$', fontsize=10)
ax1.text(0.5, 0.28, r'$10^{-12}$', fontsize=10)
# fourth column
ax1.text(0.79, 0.8, 'rel.tol.', fontsize=10)
ax1.text(0.8, 0.68, r'$10^{-3}$', fontsize=10)
ax1.text(0.8, 0.58, r'$10^{-3}$', fontsize=10)
ax1.text(0.8, 0.48, r'$10^{-6}$', fontsize=10)
ax1.text(0.8, 0.38, r'$10^{-8}$', fontsize=10)
ax1.text(0.8, 0.28, r'$10^{-12}$', fontsize=10)

ax1.spines['left'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_xticks([])
ax1.set_yticks([])


# tight layout
#plt.legend(loc=2)
ax.set_xlabel('Acceptance Threshold for matching State Trajectories', fontsize=fontsize)
ax.set_ylabel('Matching models', fontsize=fontsize)
#ax.tight_layout()

# show plot
plt.show()
