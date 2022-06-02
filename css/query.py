if report_type == 'picking':
            sm_wh = self._get_stock_move_condition()
            wh = (
                'picking_names',
                f'''SELECT
                    STRING_AGG(DISTINCT subq_sp.name, ',') documents,
                    subq_sp.scheduled_date date_picking,
                    NULL date_invoice
                FROM
                    stock_move subq_sm
                    LEFT JOIN stock_picking subq_sp ON subq_sm.picking_id = subq_sp.id
                WHERE
                    subq_sm.sale_line_id = sol.id AND
                    {sm_wh}
                GROUP BY 
                    subq_sp.scheduled_date
                ORDER BY
                    subq_sp.scheduled_date
                LIMIT 1
                ''',
                '''so.type_order = 'remision' AND 
                    so.state = 'done' AND 
                    sol.qty_x_invoiced > 0.0 AND
                    sol.price_subtotal > 0.0 AND 
                    sol.qty_received > 0.0 AND 
                    sol.product_so_qty > 0.0 
                '''
            )
        else:
            ai_wh = self._get_account_invoice_condition()
            wh = (
                'invoice_names',
                f'''SELECT
                    STRING_AGG(DISTINCT subq_ai.number, ',') documents,
                    NULL date_picking,
                    subq_ai.date_invoice date_invoice
                FROM
                    account_invoice_line subq_ail
                    LEFT JOIN account_invoice subq_ai ON subq_ail.invoice_id = subq_ai.id
                WHERE
                    subq_ail.sale_line_id = sol.id AND
                    {ai_wh}
                GROUP BY 
                    subq_ai.date_invoice
                ORDER BY
                    subq_ai.date_invoice
                LIMIT 1
                ''',
                '''so.type_order = 'reserved' AND 
                    so.state IN ('done', 'close') AND 
                    sol.qty_x_picking > 0.0 AND
                    sol.price_subtotal > 0.0 AND 
                    sol.qty_invoiced > 0.0 AND 
                    sol.product_so_qty > 0.0 
                '''
            )

        cr.execute(f'''INSERT INTO report_sale_order_picking_invoice_analysis
                            (create_date, create_uid, write_date, write_uid, name, product_id, order_id, product_so_qty,
                            uom_so_id, product_qty, uom_id, price_unit, discount, price_subtotal, price_total, price_tax, price_tax_remision,
                            qty_received, qty_invoiced, qty_transfer, qty_x_invoiced, price_x_invoiced, qty_x_picking,
                            partner_id, currency_id, date_planned, date_order, date_picking, date_invoice, contract_id,
                            model_id, uen_id, customer_category_id, customer_group_id, customer_calification_id,
                            line_analytic_id, division_id, segmento_id, analytic_id, analytic_category_id,
                            analytic_sucursal_id, zona_id, user_id, location_id, report_type, {wh[0]})
                        SELECT
                            '{dt_now}',
                            {uid},
                            '{dt_now}',
                            {uid},
                            sol.name,
                            sol.product_id,
                            sol.order_id,
                            sol.product_so_qty,
                            sol.uom_so_id,
                            sol.product_qty,
                            sol.uom_id,
                            sol.price_unit,
                            sol.discount,
                            sol.price_subtotal,
                            sol.price_total,
                            sol.price_tax,
                            (sol.qty_x_invoiced*sol.price_tax/sol.product_so_qty) as price_tax_remision,
                            sol.qty_received,
                            sol.qty_invoiced,
                            sol.qty_transfer,
                            sol.qty_x_invoiced,
                            sol.price_x_invoiced,
                            sol.qty_x_picking,
                            sol.partner_id,
                            sol.currency_id,
                            sol.date_planned,
                            sol.date_order,
                            DATE(subq.date_picking),
                            DATE(subq.date_invoice),
                            sol.contract_id,
                            sol.model_id,
                            sol.uen_id,
                            sol.customer_category_id,
                            sol.customer_group_id,
                            sol.customer_calification_id,
                            sol.line_analytic_id,
                            sol.division_id,
                            sol.segmento_id,
                            sol.analytic_id,
                            sol.analytic_category_id,
                            sol.analytic_sucursal_id,
                            sol.zona_id,
                            sol.user_id,
                            sol.location_id,
                            '{report_type}',
                            COALESCE(subq.documents, '')
                        FROM
                            sale_order_line sol
                            INNER JOIN sale_order so ON sol.order_id = so.id
                            LEFT JOIN LATERAL (
                                {wh[1]}
                                ) subq ON TRUE
                        WHERE
                            {wh[2]}
                        ''')