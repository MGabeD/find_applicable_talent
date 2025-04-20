## Running the application locally
To run this application navigate to and start **both** the front end and backend server to run this on local host

### Frontend Setup
Navigate to:
```bash
cd src/front_end/front_end/ 
```
Then install your dependencies and start the development server
```bash
npm install
npm run dev
```

### Backend Setup

For the backend make sure to set up your python interpreter. Then use the pyproject.toml to make your wheel. **NOTE:** you must be in the top level directory for the next command
```bash
python -m pip install -e .
```
Next, navigate to the backend server and start it
```bash
cd src/find_applicable_talent/backend_interface
uvicorn find_applicable_talent.backend_interface.main:app --reload
```
### Playing with the application
I created a logger which can write to both files and to console for the backend server and while I didn't de-clutter the code if you want to create new APIs it is very helpful for getting visibility and a clear history of where in the applications flow you are when edge cases occur. I suggest using it since its there and is better than printing. 

As the frontend is next it defaults to localhost:3000

As the backend is fastapi it defaults to localhost:8000

Everything is separated fairly simply so editing should be really quick and the structure is relatively independant making it easy to expand if you wanted to while playing with it.
