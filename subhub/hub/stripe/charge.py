#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json

from attrdict import AttrDict
from subhub.hub.stripe.abstract import AbstractStripeHubEvent
from subhub.hub.routes.static import StaticRoutes
from subhub.log import get_logger

logger = get_logger()


class StripeChargeSucceededEvent(AbstractStripeHubEvent):
    def run(self):
        data = self.create_data(
            charge_id=self.payload.id,
            invoice_id=self.payload.data.object.invoice,
            customer_id=self.payload.data.object.customer,
            order_id=self.payload.data.object.metadata.get("order_id", None),
            card_last4=self.payload.data.object.payment_method_details.card.last4,
            card_brand=self.payload.data.object.payment_method_details.card.brand,
            card_exp_month=self.payload.data.object.payment_method_details.card.exp_month,
            card_exp_year=self.payload.data.object.payment_method_details.card.exp_year,
            application_fee=self.payload.data.object.application_fee,
            transaction_amount=self.payload.data.object.amount,
            transaction_currency=self.payload.data.object.currency,
            created_date=self.payload.created,
        )
        routes = [StaticRoutes.SALESFORCE_ROUTE]
        self.send_to_routes(routes, json.dumps(data))