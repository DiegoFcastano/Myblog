cr = self._cr
cr.execute(f''' 
            UPDATE
                
            FROM account_invoice ai 
            INNER JOIN account_journal aj ON ai.journal_id = aj.id 
            WHERE 
                aj.id = 538
                ai.number LIKE '%E127%'
        ''')
