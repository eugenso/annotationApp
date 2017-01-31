class tableBuilder:
    """
    A class to build LaTeX tables from python lists.

    """

    def createRows(self, rows, hline):
        decoratedRows = map(lambda r: ' & '.join(r), rows)
        if hline:
            rowEnding = '\\\\ \n \hline \n'
        else:
            rowEnding = '\\\\ \n'
            #
        return rowEnding.join(decoratedRows)


    def createSimpleHeader(self, headline, frame):
        if frame:
            topline = '\hline'
            format = 'c'.join(['|']*(len(headline)+1))
        else:
            topline = ''
            format = '|'.join(['c']*len(headline))
            #
        header = [#'\\begin{table}[ht]',
                  '\\begin{tabular}{'+format+'}',
                  topline,
                  ' & '.join(headline)+'\\\\ \n \hline']
        return '\n'.join(header)


    def createSimpleFooter(self, frame):
        if frame:
            bottomLine = '\\\\ \hline'
        else:
            bottomLine = ''
        footer = [bottomLine,
                  '\end{tabular}',
                  #'\end{table}'
        ]
        return '\n'.join(footer)


    def createSimpleTable(self, content, frame, path):
        """
        content has to be a list of lists, where the first list holds the
        column names of the table.

        frame is a Boolean that indicates whether or not to put a
        frame around the table.

        """
        content = map(lambda l: map(lambda s: str(s), l), content)
        #
        header = self.createSimpleHeader(content[0], frame)
        rows = self.createRows(content[1:], True)
        footer = self.createSimpleFooter(frame)

        tex = '\n'.join([header, rows, footer])
        print tex
        with open(path, 'w+') as file:
            file.write(tex)
