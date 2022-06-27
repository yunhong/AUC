# Program to compute click-AUC
# Input are records with three possible formats:
# unweighted --> (score, label)
# weighted --> (score, label, weight)
# impclk --> (score, impressions, clicks)
# for each of the above three formats, specify the position of each field
# The fields of each record are separated by TAB

TOKEN_SEP = '\t' # the field separation token, default TAB
DEBUG = False
FLD_SCORE = 0 # the field where score is stored, default 0
FLD_LABEL = 1 # the filed where label is stored, default 1
FLD_WEIGHT = 2 # the field where weight is stored, default 2
(FLD_IMP, FLD_CLK) = (1, 2) # default field for imp and clk
(flag_unweighted, flag_weighted, flag_impclk) = (False, False, False)

def parseArgs(argv):

    global flag_unweighted, flag_weighted, flag_impclk;
    global FLD_SCORE, FLD_LABEL, FLD_WEIGHT, FLD_IMP, FLD_CLK;

    # Parse input parameters
    # from sys import argv
    i=0
    while(i<len(argv)):
        arg = argv[i].lower()
        if(arg == '-f'):
            i+=1; infile = argv[i]
        elif(arg == '-u'):
            flag_unweighted = True
            i+=1; FLD_SCORE = int(argv[i])
            i+=1; FLD_LABEL = int(argv[i])
        elif ((arg == '-w') or (argv == '-weighted')):
            flag_weighted = True
            i+=1; FLD_SCORE  = int(argv[i])
            i+=1; FLD_LABEL  = int(argv[i])
            i+=1; FLD_WEIGHT = int(argv[i])        
        elif (arg == '-impclk'):
            flag_impclk = True
            i+=1; FLD_SCORE = int(argv[i])
            i+=1; FLD_IMP = int(argv[++i])
            i+=1; FLD_CLK = int(argv[++i])
        elif ((arg == '-h') or (arg == '-help')):
            msg_help = "Program to compute Click-AUC, Usage:\n" + \
                       "python auc.py -f infile [-u fld_score fld_label] [-w[eighted] fld_score fld_label fld_weight]\n" + \
                "[-impclk fld_score fld_imp fld_clk] [-h | -help]"
            print(msg_help)
            exit()
        i+=1

    if(flag_unweighted):
        msg_param = "-unweighted fld_score " + str(FLD_SCORE) + " fld_label " + str(FLD_LABEL)    
    elif(flag_weighted):
        msg_param = "-weighted fld_score " + str(FLD_SCORE) + " fld_label " + str(FLD_LABEL) + " fld_weight " + str(FLD_WEIGHT)
    elif(flag_impclk):
        msg_param = "-impclk fld_score " + str(FLD_SCORE) + " fld_imp " + str(FLD_IMP) + " fld_clk " + str(FLD_CLK)

    if(DEBUG):
        print('python' + ' ' + argv[0] + ' -f ' + infile + ' ' + msg_param)
    
    return infile


def parseInput(infile):

    global flag_unweighted, flag_weighted, flag_impclk
    global FLD_SCORE, FLD_LABEL, FLD_WEIGHT, FLD_IMP, FLD_CLK
    
    # Parse input file and store records in a list
    fp = open(infile)
    list_record_init = []
    for line in fp:
        tokens = line.split(TOKEN_SEP)
        if ((len(tokens) < 2) or ((flag_weighted or flag_impclk) and len(tokens) < 3)):
            print('discard invalid input record: ' + line)
            continue # skip invalid record

        score = float(tokens[FLD_SCORE].strip())
        if(flag_unweighted or flag_weighted):        
            label = tokens[FLD_LABEL].strip()
            if(DEBUG):
                print(FLD_LABEL)
                print(tokens)
                print(label)
            pos = int(label)
            neg = 1 - pos
            if(flag_weighted):
                weight = int(tokens[FLD_WEIGHT])
                pos *= weight
                neg *= weight
        elif(flag_impclk):
            imp = int(tokens[FLD_IMP].strip())
            clk = int(tokens[FLD_CLK].strip())
            neg = imp - clk
            pos = clk
        record = (score, neg, pos)
        list_record_init.append(record)

    # if not sorted, sort records with decreasing SCORE
    # inplace sorting, linear time if the list is already sorted
    list_record_init.sort(key=lambda record: record[0], reverse=True)


    # Combine records with equal score into (neg, pos) counts
    record_tmp = (-1, 0, 0)
    list_record = []
    for record in list_record_init:
        (score, neg, pos) = record
        (score_tmp, neg_tmp, pos_tmp) = record_tmp
        if (score != score_tmp):
            if (score_tmp >= 0):
                list_record.append(record_tmp)
            # else score_tmp == -1, the initial step, no action needed
            record_tmp = record
        else:
            neg_tmp += neg
            pos_tmp += pos
            record_tmp = (score_tmp, neg_tmp, pos_tmp)

    if(record_tmp[0] >=0):
        list_record.append(record_tmp)

    return list_record;


def calAUC(list_record):
    # Calculat the click-auc
    (s_neg, s_pos, s_area) = (0, 0, 0)

    for record in list_record:
        (score, neg, pos) = record

        s_neg_pre = s_neg
        s_pos_pre = s_pos
        s_neg = s_neg_pre + neg
        s_pos = s_pos_pre + pos

        area = neg * (s_pos_pre + pos/2)
        s_area += area

    if(s_neg * s_pos == 0):
        print('Degenerated input, #neg=' + str(s_neg) + ', #pos=' + str(s_pos))
        auc = 0;
    else:
        auc = s_area / (s_neg * s_pos)

    if(DEBUG):
        print('Click-AUC:\t' + str(auc))
    return auc;


def main(args):
    infile = parseArgs(args);
    list_record = parseInput(infile);
    auc = calAUC(list_record);
    if(DEBUG): print(auc)
    return auc;

if __name__ == "__main__":
    import sys;
    main(sys.argv)

