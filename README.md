# kivy-tasks-server
### Description:
This application is an API server that is used to store, serve and manage data for the **_kivy-tasks-client_** application. It will use **MongoDB** and will follow the **HATEOAS** constraints as closely as possible.

REST guides and references used:
- https://en.wikipedia.org/wiki/HATEOAS
- http://www.narwhl.com/
- https://developer.paypal.com/docs/integration/direct/paypal-rest-payment-hateoas-links/

### Install steps:
- install MongoDB according to [this documentation](https://docs.mongodb.org/getting-started/shell/installation/).
- install ```pymongo``` and ```flask``` using **pip3**
