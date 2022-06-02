cr = self._cr
cr.execute(f''' UPDATE
                        stock_move 
                SET
                        cost = 32977.34,
                        costo_total = 395,728.08
                WHERE
                        id = 987038
        ''')