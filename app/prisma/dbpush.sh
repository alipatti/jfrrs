# script to generate both python and javascript clients for the JFRRS database

echo "---------- Generating javascript client... ----------\n"
export PRISMA_CLIENT_PROVIDER="prisma-client-js"
npx prisma db push

echo "---------- Generating python client... ----------\n"
export PRISMA_CLIENT_PROVIDER="prisma-client-py"
source .venv/bin/activate  # activate virtual environment
python3 -m prisma db push
