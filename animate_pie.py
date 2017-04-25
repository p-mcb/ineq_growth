import numpy as np
import pandas as pd

def load_data():
    """
    Function to read two csv files with data 
    from the World Wealth and Income Database
    http://wid.world/

    called below in make_animation()
    """

    def parse_file(fname):
        p90p100, p99p100, p0p50, p50p90 = {}, {}, {}, {}

        with open('income.shares.csv') as file:
            for line in file:
                pctl, year, share = line.rstrip('\n').split(';')
                if pctl == 'p90p100': dd = p90p100
                elif pctl == 'p99p100': dd = p99p100
                elif pctl == 'p0p50': dd = p0p50
                elif pctl == 'p50p90': dd = p50p90
                else: continue
                if share == '': share = np.nan
                dd[int(year)] = float(share)

        out = pd.DataFrame(
                {'99+':p99p100, 
                '90-99':p90p100,
                '50-90':p50p90,
                '0-50': p0p50} )

        return out

    # income distribution     
    income = parse_file('income.shares.csv')    

    income.loc[2012,'0-50'] *= 0.1                      # add zeros
    income['99+'][income['99+'] > 0.8] *= 0.1

    income['90-99'] = income['90-99'] - income['99+']   # WID data overlaps

    for x in [1963, 1965]:                              # missing for 63 & 65
        income.loc[x, '50-90'] = 1-np.nansum(income.loc[x,]) 

    # national income
    gdp = []
    with open('income.csv') as file:
        for line in file:
            year, data = line.rstrip('\n').split(',')
            gdp += [float(data)]

    income['gdp'] = gdp

    return income



def make_animation(fname = None):
    """
    A function that creates an animated pie chart. Then:
    - if given a filename, saves the animation as a gif
    - otherwise, displays the animation
    WARNING saving the gif may take a minute
    """

    def update(year):
        """
        This function is passed to FuncAnimation constructor
        & is used to to update the chart
        argument should be an index for the DataFrame income,
        which is returned by load_data() above
        """
    
        type = sum(np.isnan(income.loc[year,]))
    
        if type == 0:                        # no missing data
            data = income.loc[year, ]
            data /= sum(data)                # corrects rounding errors
            labs = income.columns
            col_list = ['b','g','m','c']
    
        elif type == 2:                      # missing below 90
            data = [ income.loc[year,'99+'],
                        income.loc[year,'90-99'],
                        1-(income.loc[year,'99+']+income.loc[year,'90-99']) 
                   ]
            labs = ['99+', '90-99', '']
            col_list = ['b','g','w']
    
        elif type == 3:                      # missing below 99
            data = [ income.loc[year,'99+'], 1-income.loc[year,'99+'] ]
            labs = ['99+', '']
            col_list = ['b', 'w']
    
        else: pass

        nonlocal ax, fig                     # update matplotlib objects
        fig.delaxes(ax)  
        ax = fig.add_subplot(111)
   
        pchart = ax.pie(
            data,
            labels = labs,
            shadow = False,
            startangle = 90,
            autopct='%1.1f%%',
            colors = col_list,
            radius = rad[year]
        )

        ax.axis('equal')

        plt.title(year, loc='left')
        plt.title('Income by Percentile')
        plt.title('Data: WID', loc='right')

        ax_lim = np.ceil(np.max(rad))
        ax.set_xlim(-ax_lim, ax_lim)
        ax.set_ylim(-ax_lim, ax_lim)

        return pchart




    income = load_data()                     # read from file             

    rad = np.sqrt(income['gdp'])             # scale chart area to gdp
    rad *=  1.25/np.max(rad)                 # 1.25 for window fitting

    income = income[['99+', '90-99', '50-90', '0-50']]  # order for chart

    import matplotlib.pyplot as plt	
    fig, ax = plt.subplots()

    pchart = update(income.index[0])

    import matplotlib.animation as animation
    anim = animation.FuncAnimation(fig, func = update, 
        frames = income.index, repeat_delay=2000)

    if fname:
        anim.save(fname, dpi=80, writer='imagemagick')
    else:
        plt.show()
        



