<h2>ConnectMe | A Tiny Scalable Blog</h2>
<p>ConnectMe is a simple blog that implements user registration and session management securely with a focus on code reusability. <!-- Go to the website to try it out. --></p>
<hr>
<h3>Features</h3>
<ul>
	<li>User signup, login and logout pages.</li>
	<li>Ability to add a new post or delete exiting posts.</li>
	<li>View posts by all users.</li>
	<li>Generates a shareable permalink on Facebook for each new post.</li>
</ul>
<hr>
<h3>Scalibility</h3>
<ul>
	<li>Robust user session verification through cryptographically hashed cookies.</li>
	<li>Secure user password storage using a salt on SHA256. Refer to _main.py and hash_secure.py</li>
	<li>Allows user information verification during registration.</li>
</ul>
<hr>
<h3>Reusability</h3>
<ul>
	<li>web_template.py - A template for any new web application on GAE.</li>
	<li>verify.py - Includes useful user information verification functions.</li>
	<li>hash_secure.py - Useful functions for cookie authentication using HMAC and encrypted password generation and verification using SHA256.</li>
</ul>
<hr>
<h3>Built Using</h3>
<ul>
	<li>webapp2</li>
	<li>Google App Engine and Data Store</li>
	<li>Jinja2</li>
	<li>Bootstrap</li>
</ul>
<hr>

<h3>Future Ideas</h3>
- Add CAPTCHA during user registration
- Add a User Profile Page to update user information.
- Infinite Possibilites

Please shoot me an email for any questions or comments.

Author - bagarwa2