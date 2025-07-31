FROM node:20-alpine

WORKDIR /app
COPY server /app/server
COPY client /app/client

WORKDIR /app/server
RUN npm install

EXPOSE 3000
CMD ["npm", "start"]