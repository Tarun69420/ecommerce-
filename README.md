# An Ecommerce Website
#### Video Demo: <[URL](https://youtu.be/27Ntxz5phZs)>
#### Description:

Creating an ecommerce website involves developing a platform that allows users to browse, search, and purchase products online. The provided codebase demonstrates a fully functional ecommerce application using Flask, a lightweight web framework in Python, integrated with a SQLite database for data storage. Here’s a detailed overview of the features and functionalities implemented in this ecommerce website.

Overview of Features
User Authentication and Management
The application allows users to register, log in, and log out securely. User credentials are stored securely using hashed passwords, managed by the werkzeug.security library. The login and registration routes handle user authentication, ensuring that sensitive data is encrypted and protected.

Product Catalog and Search Functionality
The product catalog displays all items available in the warehouse database. Users can search for products by name using the search bar, which dynamically updates the displayed items based on the search query. This enhances the user experience by providing an easy way to find specific products.

Shopping Cart and Wishlist
The application features a shopping cart and wishlist system, allowing users to add, update, and remove items. Users can add products to their cart or wishlist directly from the product catalog or product detail pages. The cart and wishlist quantities are managed efficiently, ensuring that the displayed totals reflect the actual data stored in the database.

Order Management and Checkout Process
Users can review their cart contents and proceed to checkout, where they can choose between Cash on Delivery (COD) or online payment options. Upon placing an order, the product quantities are updated in the warehouse database, and the cart is cleared. This ensures inventory accuracy and provides a seamless transition from shopping to order placement.

Session Management and User Personalization
The application uses Flask-Session to manage user sessions, storing session data on the server side. This ensures that user-specific data, such as cart contents and wishlist items, persist across different pages and browsing sessions. Additionally, the website displays personalized information, such as the user’s name and their cart and wishlist totals, enhancing the user experience.

Detailed Functionality
Index Route (/)
The index route serves as the homepage, displaying all products from the warehouse. If a user is logged in, their username, cart, and wishlist information are also retrieved and displayed. This provides a comprehensive view of available products along with user-specific data, encouraging users to continue shopping.

Search Route (/search)
The search functionality allows users to find products by name. The search term is used to query the warehouse database, returning matching results. This feature is crucial for enhancing user experience by making it easy to locate specific items among potentially thousands of products.

Login and Logout Routes (/login and /logout)
The login route handles user authentication, verifying credentials against the stored data. Upon successful login, the user’s session is initialized. The logout route clears the user session, ensuring that sensitive data is not accessible after logging out.

Product Detail Route (/product)
This route displays detailed information about a specific product, including images, descriptions, prices, and availability. Users can add the product to their cart or wishlist directly from this page, facilitating quick and easy shopping decisions.

Cart and Wishlist Management (/cart, /wishlist)
These routes manage the user’s cart and wishlist. Users can view all items in their cart or wishlist, update quantities, and remove items. The cart and wishlist are essential features for any ecommerce site, providing users with the ability to manage their desired purchases and plan future buys.

Add to Cart and Wishlist (/addcart, /add_to_wishlist)
These routes handle adding items to the cart or wishlist. The system checks for product availability in the warehouse and updates the respective database tables accordingly. If the product is already in the cart or wishlist, the quantity is incremented; otherwise, a new entry is created.

Checkout and Order Placement (/checkout, /cod, /onlinepay)
The checkout route allows users to review their cart before placing an order. Users can choose their payment method and confirm their purchase. Upon order confirmation, the system updates the warehouse inventory and clears the user’s cart, ensuring accurate stock management.

Profile Management (/profile)
The profile route displays user-specific information, including their order history and personal details. This enhances user engagement by providing a personalized experience and easy access to their data.

Conclusion
This ecommerce website exemplifies a robust and user-friendly platform for online shopping. By integrating essential features such as user authentication, product catalog, search functionality, cart and wishlist management, and secure checkout processes, the application ensures a seamless and enjoyable shopping experience. The use of Flask and SQLite provides a lightweight yet powerful framework for developing and managing the site, making it a versatile solution for ecommerce needs.






