# Setup Guide - Getting Your Frontend Running

## Prerequisites Check

First, let's make sure you have Node.js installed (this includes npm).

## Step-by-Step Setup

### Step 1: Check if Node.js is Installed

Open your terminal and run:
```bash
node --version
npm --version
```

**If you see version numbers** (like `v20.x.x` and `10.x.x`), you're good! Skip to Step 2.

**If you get an error**, you need to install Node.js:
- **macOS**: Install using Homebrew: `brew install node`
- **Or download from**: https://nodejs.org/ (get the LTS version)

### Step 2: Navigate to Your Project Folder

In your terminal, go to the View folder:
```bash
cd /Users/wiyalin/ReccarmendFullStack/View
```

### Step 3: Install All Dependencies

This downloads all the libraries your project needs:
```bash
npm install
```

**This will take a few minutes** - it's downloading all the packages listed in `package.json`.

**What you'll see:**
- Progress bars showing packages being downloaded
- May take 2-5 minutes depending on your internet speed
- When done, you'll see a message like "added 500 packages"

### Step 4: Create Environment File (For Later - Backend Connection)

The app needs Supabase credentials, but we'll create a placeholder file so it doesn't crash:

Create a file named `.env` in the View folder with:
```
VITE_SUPABASE_URL=placeholder
VITE_SUPABASE_PUBLISHABLE_KEY=placeholder
```

**Note**: We'll update these with real values when connecting to the backend later.

### Step 5: Start the Development Server

Run this command:
```bash
npm run dev
```

**What happens:**
- Vite starts a local development server
- You'll see a message like: `Local: http://localhost:8080/`
- The server is now running!

### Step 6: Open in Browser

1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: `http://localhost:8080`
3. You should see your ReCarmmend website!

### Step 7: Make a Test Change (Optional)

1. Open `src/pages/Index.tsx`
2. Find the heading text (around line 17-19)
3. Change "Find Your Perfect Car with AI" to something like "My Test Change"
4. Save the file
5. **Watch your browser** - it should automatically update! (This is called "hot reload")

## Troubleshooting

### Problem: "command not found: npm"
**Solution**: Node.js isn't installed. Install it from nodejs.org

### Problem: "EACCES" or permission errors
**Solution**: Don't use `sudo`. Instead, fix npm permissions:
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
```

### Problem: Port 8080 already in use
**Solution**: Kill the process using that port, or change the port in `vite.config.ts`

### Problem: Lots of errors in terminal
**Solution**: 
1. Delete `node_modules` folder: `rm -rf node_modules`
2. Delete `package-lock.json`: `rm package-lock.json`
3. Run `npm install` again

### Problem: Website shows errors in browser
**Solution**: 
1. Check the browser console (Press F12, go to Console tab)
2. Look for red error messages
3. Common issue: Missing `.env` file - create it as shown in Step 4

## What Each Command Does

- `npm install` - Downloads all dependencies to `node_modules/` folder
- `npm run dev` - Starts development server with hot reload
- `npm run build` - Creates production-ready files (for later deployment)
- `npm run lint` - Checks your code for errors

## Next Steps

Once you see the website running:
1. ✅ Explore the different pages (Home, Login, Signup)
2. ✅ Try clicking around the interface
3. ✅ Make small changes to see how it works
4. ⏭️ Later: Connect to your backend (Supabase)

## Stopping the Server

When you're done:
- Press `Ctrl + C` in the terminal
- This stops the development server

---

**You're all set!** 🎉 Your frontend is now running locally.



