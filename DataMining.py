"""
Data Mining Programming Assignment

This script aims to discover approximate functional dependencies in a given 
data set.
"""
import sys

def orderDomains(FD, input_data):
    """Key function for ordering the domains of attributes:
    An FD is of form [domain, attribute, support].
    want to order first by length of domain, then by the attributes of the domain
    (according to dictionary ordering, with attributes ordered as they appear in input_data),
    and finally by the attribute (again, ordered as in input_data).

    By "ordered as in input_data" we mean
    input_data[0].index(attr)
    i.e. order attributes according to the order induced by input_data[0]

    This done via the order isomorphism {0,...,N-1}x{0,...,M-1}->{0,...,NM-1}
    defined by (n,m)-> nM+m.
    More generally, we have an iso {0,...,N-1}*->Naturals defined by
    (n_1,n_2,...n_m)-> n_1*N^(m-1)+...+n_(m-1)*N+n_m

    Here n_1 will be len(domain), n_m will represent attribute,
    and [n_2,...,n_(m-1)] represents domain.
    """
    num_of_attr = len(input_data[0])
    domain = FD[0]
    dom_size = len(domain)
    attribute = FD[1]

    #initialize the result with n_m
    result = input_data[0].index(attribute)

    #add in the terms n_2*N^(m-1)+...+n_(m-1)*N
    index = 1
    while index <= dom_size:
        index_value = input_data[0].index(domain[-1*index])
        result += index_value*num_of_attr**index
        index += 1

    #add the term n_1*N^m
    result += dom_size*num_of_attr**(dom_size+1)

    return result    

def pprint(FDs):
    """Prity print of discovered FDs;
    print the FDs with formatting
    '{comma-separated domain attributes}->Attribute with support X'
    """
    print('Discovered FDs:')
    for fd in FDs:
        #case where no domain attributes
        if len(fd[0]) == 0:
            outstring = '{}->'+fd[1]+' with support '+str(fd[2])
            print(outstring)

        #case where exactly one domain attribute
        elif len(fd[0]) == 1:
            outstring ='{'+fd[0][0]+'}->'+fd[1]+' with support '+str(fd[2])
            print(outstring)
        #remaining cases (must comma-separate)
        else:
            outstring = '{'+fd[0][0]
            for attribute in fd[0][1:]:
                outstring += ','+attribute
            outstring += '}->'+fd[1]+' with support '+str(fd[2])
            print(outstring)
            
    return None

def load_data(data_file_name):
    """Read data from data_file_name and return a list of lists, 
    where the first list (in the larger list) is the list of attribute names, 
    and the remaining lists correspond to the tuples (rows) in the file.
    """
    with open(data_file_name, 'r') as f:
        almost_results = []
        for line in f:
                words = line.split(',')
                words = [word.rstrip('\n') for word in words] #get rid of the pesky newlines
                almost_results.append(words[:])

    #get rid of empty lines resulting from newline-only lines#
    results = [line for line in almost_results if not line == ['']] 
    return results

def attributeIndices(domain, input_data):
    """find the indices of input_data[0] of the attributes in domain"""
    
    index_list = []
    for attribute in domain:
        index_list.append(input_data[0].index(attribute))
    return index_list

def support(domain, attribute, input_data):
    """calculate the support of the relation domain-> attribute according to the input_data"""
    index_list = attributeIndices(domain, input_data)
    attribute_index = input_data[0].index(attribute)
    num_sum = 0
    denom_sum = 0

    #create a dictionary with keys=input-tuples and 
    #values=dictionary of attribute-values and the number of occurrences
    counter = dict()
    for item in input_data[1:]:

        #isolate the input from the input_data by getting only those
        #associated with the attributes from domain
        fd_input = []
        for index in index_list:
            fd_input.append(item[index])

        #make it a tuple so it can be a key in a dictionary    
        cast_input = tuple(fd_input)

        #add the attribute-value to the value-dictionary associated with fd_input
        #case 1: cast_input hasn't appeared yet, so initialize value-dictionary
        if not cast_input in counter:
            counter[cast_input] = {item[attribute_index]: 1}
        #case 2: cast_input has appeared, but this value hasn't, so initialize that value's occurrence
        elif not item[attribute_index] in counter[cast_input]:
            counter[cast_input][item[attribute_index]] = 1
        #case 3: cast_input and this value have appeared, so increment that value's occurrences
        elif item[attribute_index] in counter[cast_input]:
            counter[cast_input][item[attribute_index]] += 1

        #print([cast_input,counter[cast_input]])

    #for each fd_input calculate the contributions to num and denom of support
    for fd_input in counter:
        #get number of instances of most common value associated with fd_input
        max_instances = max(list(counter[fd_input].values()))

        #get total number of instances of values associated with fd_input
        total_instances = sum(list(counter[fd_input].values()))

        #add these to numerator and denominator of support
        num_sum += max_instances
        denom_sum += total_instances

    #calculate support after every fd_input has been examined
    quotient = num_sum/denom_sum
    
    return quotient

def attributeOrdering(domain, attribute, input_data):
    """determine whether the attribute comes after those in domain, according to
    those in input_data"""

    if domain == []:
        larger = True
    else:
        domain_indices = attributeIndices(domain, input_data)
        largest_domain_index = max(domain_indices)

        attribute_index = input_data[0].index(attribute)

        if largest_domain_index < attribute_index:
            larger = True
        else:
            larger = False
    
    return larger

def find_approximate_functional_dependencies(data_file_name, depth_limit, minimum_support):
    """Main function which you need to implement!
    
    The function discovers approximate functional dependencies in a given data
    
    Input:
        data_file_name - name of a CSV file with data 
        depth_limit - integer that limits the depth of search through the space of 
            domains of functional dependencies
        minimum_support - threshold for identifying adequately approximate FDs
        
    Output:
        FDs - a list of tuples. Each tuple represents a discovered FD.
        The first element of each tuple is a list containing LHS of discovered FD
        The second element of the tuple is a single attribute name, which is RHS of that FD
        The third element of the tuple is support for that FD
    
    Output example:
        [([A],C, 0.91), ([C, F],E, 0.97), ([A,B,C],D, 0.98), ([A, G, H],F, 0.92)]
        The above list represent the following FDs:
            A -> C, with support 0.91
            C, F -> E, with support 0.97 
            A, B, C -> D, with support 0.98
            A, G, H -> F, with support 0.92                   
    """
    #read input data:
    input_data = load_data(data_file_name)
    
    #Transform attribute_values (list of lists) into some better representation.
    #You need to deside what that representation should be.
    #Data transformation is optionsal!
    
    #--------You code here! Optional! ----------#
    
    #Discover FDs with given minimun support and depth limit:
    approximate_FDs = []
    domains_frontier = [[]]
    attribute_list = input_data[0]
	
    #search through the domains_frontier in a depth-first search to test functional dependecies#
    while not domains_frontier == []:
        
        #get the next_domain, treating domain-frontier as stack#
        next_domain = domains_frontier.pop()
		
        #check if next_domain -> attribute has sufficient support#
        for attribute in attribute_list: 
            if not attribute in next_domain:
                fd_support = support(next_domain,attribute,input_data)
                if fd_support >= minimum_support:
                    approximate_FDs.append([next_domain, attribute, fd_support])
					
        current_depth = len(next_domain)
        if current_depth < depth_limit:
            for attribute in attribute_list:

                if attributeOrdering(next_domain, attribute, input_data):
                    new_domain = [x for x in next_domain]
                    new_domain.append(attribute)
                    domains_frontier.append(new_domain)

    #Order the FDs while input_data still loaded:
    approximate_FDs.sort(key=lambda FD: orderDomains(FD, input_data))
  
    return approximate_FDs

FDs = find_approximate_functional_dependencies('IndividualProjectTestSet1.csv', 4, .5)
print(FDs)
pprint(FDs)

'''
if __name__ == '__main__':
    #parse command line arguments:
    if (len(sys.argv) < 3):
        print('Wrong number of arguments. Correct example:')
        print('python find_fds.py input_data_set.csv 3 0.91')
    else:
        data_file_name = str(sys.argv[1])
        depth_limit = int(sys.argv[2])
        minimum_support = float(sys.argv[3])

        #Main function which you need to implement. 
        #It discover FDs in the input data with given minimum support and depth limit
        FDs = find_approximate_functional_dependencies(data_file_name, depth_limit, minimum_support)
        
        #print you findings:
        pprint(FDs)
'''
