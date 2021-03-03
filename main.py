from telnetCon import TelnetCon
import re
import numpy as np
import argparse
import matplotlib.pyplot as plt

#TODO timeout when heating takes too long
#TODO check whether printer is homed


def initialize():
    tc = TelnetCon(host='littlemonster.local', pw='Elena9596', db=0)
    tc.send('M98 P"0:/macros/MISC/Network/greetTelnet"')
    print(tc.tn.read_until(b'onster'))
    tc.setTemp(20)

    #runRepeatabilityTest(tc=tc, iter=20)
    #runRepeatabilityTestWithThermalCycle(tc, 3, 70, 10)

    return tc

def runRepeatabilityTest(tc, iter):
    results = []
    tc.send(('G1 X0 Y0 Z10 F 1000'))
    for i in range(iter):
        tc.send('G30 S-1')
        tc.waitForMovesToFinish()
        tc.send('G1 Z5')
        tc.waitForMovesToFinish()
        res = tc.tn.read_until(b'mm')
        res = re.findall(r'-*\d+.\d+',res.decode())[0]
        results.append(float(res))
    print(results)
    print(f'Mean: {np.mean(results)}mm\nSTD: {np.std(results)}mm\n')


def runRepeatabilityTestWithThermalCycle(tc, iter, temp_start, temp_stop, temp_step ):
    results = []
    t_steps = np.arange(temp_start, temp_stop+temp_step, temp_step).tolist()
    tc.send('G1 X0 Y0 Z10 F 1000')

    n, match, previous_text = tc.tn.expect([br'insufficient ', br'\$'],10)
    if n == 0:
        print(previous_text)
        tc.send('G28')
    else:
        print(previous_text)


    for step in t_steps:
        print(f'heating to {step} degrees')
        results2 = []
        tc.setTemp(step)
        tc.waitForHeater()
        tc.dwell(seconds=20)    #wait for temp to settle
        for i in range(iter):
            tc.send('G30 S-1')
            tc.waitForMovesToFinish()
            tc.send('G1 Z5')
            tc.waitForMovesToFinish()
            res = tc.tn.read_until(b'mm')
            res = re.findall(r'-*\d+.\d+', res.decode())[0]
            results2.append(float(res))
            print(f'probed {i+1} of {iter}')
        results.append(results2)
    tc.setTemp(0)
    means = [np.mean(r) for r in results]
    stds = [np.std(r) for r in results]
    for mean, std in zip(means, stds):
        print(f'Mean: {mean:.4f}mm\nSTD: {std:.4f}mm\n')

    plt.errorbar(t_steps,means,yerr=stds, fmt='-o')
    plt.show()
    #print(results)
    #results = [f'Mean: {np.mean(r):.4f}mm   STD: {np.std(r):.4f}mm'for r in results]
    #print(results)
    #print(f'Mean: {np.mean(results)}mm\nSTD: {np.std(results)}mm\n')



if __name__ == '__main__':
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Run repeatability tests on your Duet')

    # Add the arguments
    my_parser.add_argument('i',
                           type=int,
                           help='how often the endstop will be triggered')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    iter = args.i
    tc = initialize()
    runRepeatabilityTestWithThermalCycle(tc, iter,temp_start=50, temp_stop= 200, temp_step= 10)

