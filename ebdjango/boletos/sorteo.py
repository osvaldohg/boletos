
# coding: utf-8

# In[46]:

import os
import pandas as pd
import numpy as np
from ebdjango.settings import CSVFILES_FOLDER

localPath=os.path.join(CSVFILES_FOLDER,'lista_ganadores_2017.csv') 

# load data into a data frame
# encoding parameter set to read the data file CSV UTF-8 format
# Rename columns from Spanish to English names and set the **Prize** column as the *index*.

labels = ['Prize','Description','Winner','Ticket_Nbr','Seller','Seller_prize']
df = pd.read_csv(localPath,encoding='utf8',header=0,names=labels, index_col = 'Prize', dtype=str)

# Save the **Ticket_Nbr** column in a new df for the number repetitions analysis.

# In[47]:


df_rep = df.iloc[:, np.r_[2]]


# The dataframe information type is object64 (strings), in order to classify the tickets into ranges, it is required to convert the **Ticket_Nbr** column to numeric values.

# In[48]:


df['Ticket_Nbr'] = pd.to_numeric(df['Ticket_Nbr'])


# ## Range analysis
# 
# The objective is to find the range of numbers where most of the winner tickets can be found.
# Some columns are not required in this analysis, only columns **1 and 4** (Prize and Ticket_Nbr) are saved in a new dataframe.

# In[49]:


df_range = df.iloc[:, np.r_[2:3]]

# In[50]:


# Funtion to get the width of n bins
def get_bins_width(n):
    increment = int(280000/n)
    bins = []
    for i in range(0,n+1):
        bins.append(increment*i)
    return bins


# ## Number repetitions analysis
# 
# The goal here is to identify which numbers had a higher frequency within the winner tickets. That is if you want to buy a ticket, **what number should it include so you have a higher probability to win a prize?**

# During the raffle, each winner is known only after one ball is randomly drawn from each of the six urns. However as we can see in our data, there are some winners which have less than six digits, this means that there were zeroes ot the left that were omitted.<p>
# *For example:* After a ball is drawn from the urns, the winners is number **003476** but in our data we will find it as **3476**. In order to do the number repetition analysis, the two missing zeroes on the left should be completed.

# In[51]:


# Function that adds the necessary zeroes to make a ticket of a length equal to six
def complete_digits(ticket):
    if len(ticket) != 6:
        diference = 6-len(ticket)
        return '0'* diference + ticket
    return ticket


# In[52]:


# Apply the function previously defined through the 'Ticket Nbr' column, rename the new column as 'New_Ticket_Nbr' 
new_tkt_nbr = df_rep['Ticket_Nbr'].apply(lambda x: complete_digits(x))
new_tkt_nbr.name = 'New_Ticket_Nbr'


# In[53]:


# join the new_tkt_nbr series to the dataframe
df_rep = df_rep.join(new_tkt_nbr, lsuffix='Prize')
df_rep.head(2)


# The next function gets the frequencies of each digit in the ticket number. Frequencies are saved by position in a list i.e. the repetition of ones are kept in the `frequencies[1]` position, threes can be found in `frequencies[3]` and so on.

# In[54]:


def get_frequencies(ticket_nbr):
    frequencies = [0 for x in range(10)]
    for digit in ticket_nbr:
        frequencies[int(digit)] += 1
    return frequencies


# In[55]:


# Apply the function previously defined through the 'New_Ticket_Nbr' column, rename the new column as 'Frequencies' 
freq = df_rep['New_Ticket_Nbr'].apply(lambda x: get_frequencies(x))
freq.name = 'Frequencies'


# In[56]:


# join the freq series to the dataframe
df_rep = df_rep.join(freq, lsuffix='Prize')


# In[57]:


# Expand each element of the list in the 'Frequencies' column.
df_rep = df_rep.join(df_rep['Frequencies'].apply(lambda x: pd.Series(x)))


# In[58]:


# Sum of total appearances of a number in all the tickets.
df_total_freq = df_rep.loc[:, np.r_[0:10]].sum()


# In[59]:


# Set data frame
df_total_freq= df_total_freq.to_frame()
df_total_freq.columns = ['Frequency']
df_total_freq.index.names = ['Digit']


# It is clear that the most frequent digits of the winner tickets were **zero** and **one**. Therefore, it is better to choose a ticket that has these digits (0,1).

# Now let's see the maximun number of times a number is repeated in a ticket. This way you can have an idea if it's good to buy a ticket with a number repeated three times (i.e. **1**2**1**37**1**) instead of one with a duplicated digit (**22**7098).

# In[60]:


# Print the amount of tickets having 'x' repetitions of each digit
df_value_counts = pd.DataFrame()
for i in range(10):
    a = df_rep[i].value_counts().to_frame()
    df_value_counts =  df_value_counts.join(a, how='outer')

df_value_counts.index.name = 'Repetitions'


# In[61]:


# Replace NaN values with zero
df_value_counts = df_value_counts.fillna(0)

# # Rank a ticket

# In this section you can enter a ticket number and it will be graded based on the following scales:
#     1. Bins
#     2. Digit's frequency
#     3. Consecutive repeteated numbers

# ### 1. Points per bin bucket

# In[62]:


# Bin points
bins = get_bins_width(10)


# In[63]:


bin_pts = df['Ticket_Nbr'].value_counts(bins = bins).to_frame()
bin_pts['Points'] = bin_pts['Ticket_Nbr'].div(250)


# In[64]:


def bin_points(ticket):
    ticket = int(ticket)
    rng, i = 0,0
    while rng == 0:
        if ticket <= bins[i+1]:
            rng = bin_pts.iloc[i,1]
        else:
            i+= 1
    return rng


# ### 2. Points per digit's frequency

# In[65]:


# max frequency found in the data frame "df_value_counts"
max_freq = df_value_counts.index.max()


# In[66]:


"""" Given a ticket number (int) it returns the frequency of each one of its digits
     e.g. get_digit_freq('088546') returns  {0: 1, 4: 1, 5: 1, 6: 1, 8: 2}
"""
def get_digit_freq(ticket):
    freq = {}
    for digit in str(ticket):
        if int(digit) in freq:
            freq[int(digit)] += 1
        else:
            freq[int(digit)] = 1
    return freq


# In[67]:


def nfreq_points(ticket):
    freq = get_digit_freq(ticket)
    points = 0
    for key, value in freq.items():
        if value <= max_freq:
            points += df_value_counts.loc[value][key]
    return points/250


# ### 3. Consecutive repetead numbers

# In[68]:


""" Given a string a character the function will return the number of
    equal consecutive characters from the beginning
    e.g. input: 88546
         output: 2
"""
def count_consec(text):
    count = 1
    if len(text) > 1:
        i = 1
        while  i < len(text):
            if text[0] == text[i]:
                count +=1
                i += 1
            else:
                i = len(text)
    return count


# In[69]:


""" funcion para contabilizar los numeros iguales
    que se encuentran juntos por ejemplo
    input : str -> 088546
    output: {0: {1:1}, 8: {2:1}, 5: {1:1}, 4: {1:1}, 6: {1:1}}
"""

def count_rep(text):
    # loop trough all the characters in the text
    #i = 0
    rep_dic = {}
    while text != '':
        base = text[0]
        rep = count_consec(text)
        text = text[rep:]
        if base not in rep_dic:
            rep_dic [base] = {}
        if rep in rep_dic[base]:
            rep_dic[base][rep] += 1
        else:
            rep_dic[base][rep] = 1
    return rep_dic


# In[70]:


# Add a column with equal consecutive numbers count
df_rep['Reps'] = df_rep['New_Ticket_Nbr'].apply(lambda x: count_rep(x))

# In[71]:


# Indexes for the dataframe
repetitions = df_value_counts.index[1:].tolist()

# Columns for the dataframe
headers = []
for i in range(10):
    headers.append(i)


# In[72]:


# Create dataframe with categories and headers list
df_join = pd.DataFrame(index=repetitions, columns=headers)
df_join = df_join.fillna(0)


# In[73]:


""" This section sums up how many tickets had consecutive
    repetitions of each number"""
# loop over each number from 0 to 9
for i in range(10):
    col = i
    
    # Filter only records where repetitions of a number are equal or greater than 1
    filt_list = df_rep.loc[df_rep[col] >= 1]['Reps'].tolist()

    # Go over each record
    for row in filt_list:
        dic_join = row[str(col)]    # Dictionary of the digit (key) = col
        max_key = max(dic_join.keys())    # Max key in the dictionary, this is to avoid double counting a ticket
        df_join.loc[max_key][col] += 1


# In[74]:


# find max consecutive repetitions in the data frame "df_join"
max_consecutive = df_join.index.max()


# In[75]:


# calculate points per consecutive numbers
def consecutive_points(ticket):
    tkt_dic = count_rep(ticket)
    points = 0
    for number in tkt_dic:
        key_lst = max(tkt_dic[number].keys())
        if key_lst <= max_consecutive:
            points += df_join.loc[key_lst][int(number)]
    return(points/250)


# ## Find best ticket based on the three categories of points

# In[76]:


""" Function that given a ticket, returns the total of its points
based on the three evaluated categories: 
1. Bins
2. Digit's frequency
3. Consecutive repeteated numbers """

def all_cat_points(ticket):
    b = bin_points(ticket)
    r = nfreq_points(ticket)
    c = consecutive_points(ticket)
    return b + r + c


# In[77]:


""" Given a list of tickets, the function returns the ticket with the highest score"""
def best_ticket(ticket_list):
    points_list = []
    for ticket in ticket_list:
        ticket = str(ticket)
        total = all_cat_points(ticket)
        points_list.append(total)
    indx_best_tkt = points_list.index(max(points_list))
    return ticket_list[indx_best_tkt]


# In[78]:


""" Given a list of tickets, return the tickets and their points in descending order
based on its total score.
inputs: list of tickets (each ticket must be a string)
"""
def rank_tickets(ticket_list):
    for i in range(len(ticket_list)):
        ticket_list[i] = (ticket_list[i],)
        total = all_cat_points(ticket_list[i][0])     ## uncomment when finished with test
        #total = all_cat_points_details(ticket_list[i][0])  ## delete when finished with test
        ticket_list[i] = (ticket_list[i][0],"{0:.2f}".format(total))
    return sorted(ticket_list, key=lambda ticket: ticket[1], reverse=True)
