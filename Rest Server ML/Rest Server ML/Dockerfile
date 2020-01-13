#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/core/aspnet:3.0-buster-slim AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/core/sdk:3.0-buster AS build
WORKDIR /src
COPY ["Rest Server ML/Rest Server ML.csproj", "Rest Server ML/"]
RUN dotnet restore "Rest Server ML/Rest Server ML.csproj"
COPY . .
WORKDIR "/src/Rest Server ML"
RUN dotnet build "Rest Server ML.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Rest Server ML.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Rest Server ML.dll"]
