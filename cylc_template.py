# The run commands to run each of the tasks
commands = {'case_run': 'case.run.cylc', 'case_st_archive': 'case.st_archive', 'case_lt_archive': 'case.lt_archive',
            'timeseries': 'postprocess/timeseries', 
            'timeseriesL': 'postprocess/timeseriesL',
            'atm_averages': 'postprocess/atm_averages', 'atm_diagnostics': 'postprocess/atm_diagnostics',
            'ocn_averages': 'postprocess/ocn_averages', 'ocn_diagnostics': 'postprocess/ocn_diagnostics', 
            'lnd_averages': 'postprocess/lnd_averages', 'lnd_diagnostics': 'postprocess/lnd_diagnostics',
            'ice_averages': 'postprocess/ice_averages', 'ice_diagnostics': 'postprocess/ice_diagnostics'}


def create_cylc_input(graph, env, fn):

    cr = env['CASEROOT']
    f = open(fn, 'w')
    
    # add header
    f.write('title = '+env['CASE']+' workflow \n'+
            '[cylc]\n'+
            '    [[environment]]\n'+
            '        MAIL_ADDRESS='+env['email']+'\n'+
            '    [[event hooks]]\n'+
            '        shutdown handler = cylc email-suite\n')

    # add dependencies
    f.write('[scheduling]\n'+
            '    [[dependencies]]\n'+
            '        graph = \"\"\"\n')
    for t in graph:
            d = t.get_id()+' => '
            if len(t.depends) > 0:
                for i in range(0,len(t.depends)):
                    d = d + t.depends[i]
                    if i < len(t.depends)-1:
                        d = d + ' & '           
                f.write('                    '+d+'\n')
    f.write('               \"\"\"\n')

    # add run time - REPLACE WITH REAL DIRECTIVES
    f.write('[runtime]\n'+
            '    [[root]]\n'+
            '        pre-script = \"cd '+cr+'\"\n')
    for t in graph:
        task = t.get_id()
        task_split = task.split('_')
        tool = task_split[0]
        #print tool
        if 'atm' in tool or 'ocn' in tool or 'lnd' in tool or 'ice' in tool or 'case' in tool:
            tool = tool + '_' + task_split[1]
            if 'archive' in task_split[2]:
               tool = tool + '_' + task_split[2] 
        #print tool
        f.write('    [['+task+' ]]\n')
        f.write('        script = '+cr+'/'+commands[tool]+'\n')
        f.write('        [[[job submission]]]\n'+
                '                method = lsf\n'+
                '        [[[directives]]]\n')
        if tool == 'timeseriesL':
            for d in env['directives']['timeseries']:
                f.write('                '+d+'\n')
        else:
            for d in env['directives'][tool]:
                f.write('                '+d+'\n')
        f.write('        [[[event hooks]]]\n'+
                '                started handler = cylc email-suite\n'+
                '                succeeded handler = cylc email-suite\n'+
                '                failed handler = cylc email-suite\n')
            

def setup_suite(path, suite_name, image=None):

    import subprocess
    import os
    from shutil import copyfile

    # Make suite directory if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)

    # Copy the suite file over
    cwd = os.getcwd() 
    copyfile(cwd+'/suite.rc', path+'/suite.rc') 

    # Register the suite
    cmd = 'cylc register '+suite_name+' '+path  
    os.system(cmd)

    # Validate the suite
    cmd = 'cylc validate '+suite_name
    os.system(cmd)

    if (image):
       # Show a graph
       suffix = image.split('.')[-1]
       cmd = 'cylc graph -O '+image+' --output-format='+suffix+' '+suite_name
       os.system(cmd)

