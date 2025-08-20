# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.

# Basketna

Price comparison and tracking platform for India.

## Quick start (Docker)

1. Ensure Docker is installed
2. Run:

```bash
docker compose up
```

- API: http://localhost:8000/docs
- Web: http://localhost:5173

## Manual dev setup

- Backend
	- Python 3.11
	- `pip install -r backend/requirements.txt`
	- Generate dataset: `python scripts/generate_sample_data.py`
	- Run API: `uvicorn backend.main:app --reload`

- ML
	- Optional: `pip install -r ml/requirements.txt`
	- Run forecast script: `python -m ml.forecast P001`

- Frontend
	- Node 20+
	- `cd frontend && npm install && npm run dev`

## Notes

- Dataset at `data/sample_prices.csv` (~5 products x 4 sites x 30 days)
- Forecast images saved to `data/forecasts/` when running ML
- Authentication is basic JWT; tracking endpoints require auth
